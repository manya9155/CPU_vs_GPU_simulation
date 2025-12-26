import pygame
import numpy as np
import time
import math

# ================= CONSTANTS =================
W, H = 800, 600
WHITE = (255, 255, 255)
BG = (30, 30, 30)

VERTEX_COLORS = np.array([
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255]
], dtype=np.uint8)

# ================= SHAPES =================
def get_shape(shape):
    if shape == "triangle":
        return np.array([
            [-50, -50],
            [ 50, -50],
            [  0,  50]
        ], dtype=float)

    if shape == "square":
        return np.array([
            [-50, -50], [ 50, -50], [ 50,  50],
            [-50, -50], [ 50,  50], [-50,  50]
        ], dtype=float)

    if shape == "rectangle":
        return np.array([
            [-70, -40], [ 70, -40], [ 70,  40],
            [-70, -40], [ 70,  40], [-70,  40]
        ], dtype=float)

# ================= VECTOR EDGE FUNCTION =================
def edge(a, b, p):
    return (p[..., 0] - a[0]) * (b[1] - a[1]) - (p[..., 1] - a[1]) * (b[0] - a[0])

# ================= VECTOR RASTERIZER =================
def draw_triangle_vectorized(surface, v0, v1, v2, color):
    minx = max(int(min(v0[0], v1[0], v2[0])), 0)
    maxx = min(int(max(v0[0], v1[0], v2[0])), W - 1)
    miny = max(int(min(v0[1], v1[1], v2[1])), 0)
    maxy = min(int(max(v0[1], v1[1], v2[1])), H - 1)

    if minx > maxx or miny > maxy:
        return

    xs = np.arange(minx, maxx + 1)
    ys = np.arange(miny, maxy + 1)

    X, Y = np.meshgrid(xs, ys)
    P = np.stack([X, Y], axis=-1)

    e0 = edge(v1, v2, P)
    e1 = edge(v2, v0, P)
    e2 = edge(v0, v1, P)

    mask = ((e0 >= 0) & (e1 >= 0) & (e2 >= 0)) | \
           ((e0 <= 0) & (e1 <= 0) & (e2 <= 0))

    pixels = pygame.surfarray.pixels3d(surface)
    pixels[X[mask], Y[mask]] = color

# ================= MAIN VECTOR CPU LOOP =================
def run_cpu_vectorized(shape_name):
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("CPU VECTOR MODE (SIMD-like)")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    verts = get_shape(shape_name)
    pos = np.array([W // 2, H // 2], dtype=float)
    angle = 0.0

    MOVE = 4
    ROT = 0.08

    frame_times = []

    button_rect = pygame.Rect(W - 210, H - 60, 190, 40)
    running = True
    switch_to_gpu = False

    while running:
        t0 = time.perf_counter()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(e.pos):
                    switch_to_gpu = True
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  pos[0] -= MOVE
        if keys[pygame.K_RIGHT]: pos[0] += MOVE
        if keys[pygame.K_UP]:    pos[1] -= MOVE
        if keys[pygame.K_DOWN]:  pos[1] += MOVE
        if keys[pygame.K_r]:     angle += ROT

        c, s = math.cos(angle), math.sin(angle)
        R = np.array([[c, -s], [s, c]])
        transformed = (verts @ R.T) + pos

        screen.fill(BG)

        for i in range(0, len(transformed), 3):
            draw_triangle_vectorized(
                screen,
                transformed[i],
                transformed[i + 1],
                transformed[i + 2],
                VERTEX_COLORS[0]
            )

        fps = clock.get_fps()
        screen.blit(font.render(f"VECTOR CPU | FPS: {fps:.1f}", True, WHITE), (10, 10))
        screen.blit(font.render("NumPy SIMD-style Rasterization", True, WHITE), (10, 30))

        pygame.draw.rect(screen, (200, 70, 70), button_rect)
        screen.blit(font.render("Switch to GPU", True, WHITE),
                    (button_rect.x + 25, button_rect.y + 10))

        pygame.display.flip()
        clock.tick(60)

        frame_times.append(time.perf_counter() - t0)

    pygame.quit()

    avg_ms = sum(frame_times) / len(frame_times) * 1000
    avg_fps = 1000 / avg_ms

    return {
        "action": "gpu" if switch_to_gpu else "exit",
        "avg_ms": avg_ms,
        "avg_fps": avg_fps
    }
