import pygame
import numpy as np
import time
import math

W, H = 800, 600
WHITE = (255, 255, 255)
RED = (220, 60, 60)
BG = (30, 30, 30)

VERTEX_COLORS = np.array([
    [255, 0, 0],   # Red
    [0, 255, 0],   # Green
    [0, 0, 255]    # Blue
], dtype=float)

# ================= SHAPES =================
def draw_line_cpu(surface, x0, y0, x1, y1, color):
    x0, y0 = int(x0), int(y0)
    x1, y1 = int(x1), int(y1)

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= x0 < W and 0 <= y0 < H:
            surface.set_at((x0, y0), color)

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

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

# ================= CPU RASTERIZATION =================
def edge(a, b, c):
    return (c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])

def draw_triangle_cpu(surface, depth, v0, v1, v2, c0, c1, c2):
    minx = max(int(min(v0[0], v1[0], v2[0])), 0)
    maxx = min(int(max(v0[0], v1[0], v2[0])), W - 1)
    miny = max(int(min(v0[1], v1[1], v2[1])), 0)
    maxy = min(int(max(v0[1], v1[1], v2[1])), H - 1)

    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            p = (x, y)

            e0 = edge(v1, v2, p)
            e1 = edge(v2, v0, p)
            e2 = edge(v0, v1, p)

            if ((e0 >= 0 and e1 >= 0 and e2 >= 0) or
                (e0 <= 0 and e1 <= 0 and e2 <= 0)):

                w0, w1, w2 = barycentric(v0, v1, v2, p)

                z = w0*v0[2] + w1*v1[2] + w2*v2[2]

                if z < depth[x, y]:
                    depth[x, y] = z

                    color = (
                        w0*c0 +
                        w1*c1 +
                        w2*c2
                    ).astype(int)

                    surface.set_at((x, y), color)

def draw_wireframe_cpu(surface, v0, v1, v2):
    draw_line_cpu(surface, v0[0], v0[1], v1[0], v1[1], WHITE)
    draw_line_cpu(surface, v1[0], v1[1], v2[0], v2[1], WHITE)
    draw_line_cpu(surface, v2[0], v2[1], v0[0], v0[1], WHITE)

# ================= MAIN CPU LOOP =================
def run_cpu(shape_name):
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("CPU MODE (Pure Software Rasterizer)")

    render_mode = 0
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

    depth_buffer = np.full((W, H), np.inf, dtype=float)

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
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    render_mode = (render_mode + 1) % 3


        depth_buffer.fill(np.inf)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  pos[0] -= MOVE
        if keys[pygame.K_RIGHT]: pos[0] += MOVE
        if keys[pygame.K_UP]:    pos[1] -= MOVE
        if keys[pygame.K_DOWN]:  pos[1] += MOVE
        if keys[pygame.K_r]:     angle += ROT

        # ===== Vertex Transform (CPU) =====
        c, s = math.cos(angle), math.sin(angle)
        R = np.array([[c, -s], [s, c]])
        transformed = np.hstack([
            (verts @ R.T) + pos,
            np.zeros((len(verts), 1))
        ])


        screen.fill(BG)

        # ===== Rasterization =====
        for i in range(0, len(transformed), 3):
            v0 = transformed[i]
            v1 = transformed[i + 1]
            v2 = transformed[i + 2]

            c0 = VERTEX_COLORS[0]
            c1 = VERTEX_COLORS[1]
            c2 = VERTEX_COLORS[2]

            if render_mode == 1:
                # ✅ PURE CPU wireframe
                draw_wireframe_cpu(screen, v0, v1, v2)

            else:
                # ✅ PURE CPU filled / overdraw
                draw_triangle_cpu(
                    screen,
                    depth_buffer,
                    v0, v1, v2,
                    c0, c1, c2
                )


        # ===== UI =====
        fps = clock.get_fps()
        screen.blit(font.render(f"CPU MODE | FPS: {fps:.1f}", True, WHITE), (10, 10))
        screen.blit(font.render("Pure Software Pipeline", True, WHITE), (10, 30))

        pygame.draw.rect(screen, (70, 70, 200), button_rect)
        screen.blit(font.render("Switch to GPU", True, WHITE),
                    (button_rect.x + 20, button_rect.y + 10))

        pygame.display.flip()
        clock.tick(60)

        frame_times.append(time.perf_counter() - t0)

    pygame.quit()

    avg_ms = sum(frame_times) / len(frame_times) * 1000
    avg_fps = 1000 / avg_ms

    return {
        "action": "switch" if switch_to_gpu else "exit",
        "avg_ms": avg_ms,
        "avg_fps": avg_fps
    }

def barycentric(v0, v1, v2, p):
    area = edge(v0, v1, v2)
    w0 = edge(v1, v2, p) / area
    w1 = edge(v2, v0, p) / area
    w2 = edge(v0, v1, p) / area
    return w0, w1, w2

