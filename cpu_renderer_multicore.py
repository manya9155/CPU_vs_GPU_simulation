import pygame
import numpy as np
import time
import math
from multiprocessing import Process, Array, cpu_count

W, H = 800, 600
WHITE = (255, 255, 255)
BG = (30, 30, 30)

def edge(a, b, c):
    return (c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])

def point_in_triangle(p, v0, v1, v2):
    e0 = edge(v0, v1, p)
    e1 = edge(v1, v2, p)
    e2 = edge(v2, v0, p)

    # inside if all have same sign
    return ((e0 >= 0 and e1 >= 0 and e2 >= 0) or
            (e0 <= 0 and e1 <= 0 and e2 <= 0))

# We can’t share a pygame.Surface, so we share raw pixel memory.
def make_shared_buffer():
    # RGB buffer
    return Array('B', W * H * 3, lock=False)

# Index helper
def set_pixel(buf, x, y, color):
    idx = (y * W + x) * 3
    buf[idx]     = color[0]
    buf[idx + 1] = color[1]
    buf[idx + 2] = color[2]

# Worker rasterizer (runs in parallel)
# Each process gets:
# tile bounds
# transformed vertices
# shared buffer
def raster_worker(tile_y0, tile_y1, triangles, buffer):
    for v0, v1, v2, color in triangles:
        minx = max(int(min(v0[0], v1[0], v2[0])), 0)
        maxx = min(int(max(v0[0], v1[0], v2[0])), W - 1)
        miny = max(int(min(v0[1], v1[1], v2[1])), tile_y0)
        maxy = min(int(max(v0[1], v1[1], v2[1])), tile_y1 - 1)

        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                # simple edge test
                if point_in_triangle((x, y), v0, v1, v2):
                    set_pixel(buffer, x, y, color)

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

def run_cpu_multicore(shape_name):
    pos = np.array([W // 2, H // 2], dtype=float)
    angle = 0.0

    MOVE = 4
    ROT = 0.08

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("CPU MULTICORE MODE")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    verts = get_shape(shape_name)
    pos = np.array([W // 2, H // 2], dtype=float)
    angle = 0.0

    buffer = make_shared_buffer()

    cores = min(cpu_count(), 4)  # limit for sanity
    tile_height = H // cores

    frame_times = []
    running = True

    while running:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  pos[0] -= MOVE
        if keys[pygame.K_RIGHT]: pos[0] += MOVE
        if keys[pygame.K_UP]:    pos[1] -= MOVE
        if keys[pygame.K_DOWN]:  pos[1] += MOVE
        if keys[pygame.K_r]:     angle += ROT

        t0 = time.perf_counter()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # clear buffer
        for i in range(len(buffer)):
            buffer[i] = 0

        # vertex transform
        c, s = math.cos(angle), math.sin(angle)
        R = np.array([[c, -s], [s, c]])
        transformed = (verts @ R.T) + pos

        triangles = []
        for i in range(0, len(transformed), 3):
            triangles.append((
                transformed[i],
                transformed[i+1],
                transformed[i+2],
                (220, 60, 60)
            ))

        # spawn workers
        workers = []
        for i in range(cores):
            y0 = i * tile_height
            y1 = H if i == cores - 1 else (i + 1) * tile_height

            p = Process(
                target=raster_worker,
                args=(y0, y1, triangles, buffer)
            )
            workers.append(p)
            p.start()

        for p in workers:
            p.join()

        button_rect = pygame.Rect(W - 210, H - 60, 190, 40)
        switch_to_gpu = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(e.pos):
                    switch_to_gpu = True
                    running = False


        # blit buffer to screen
        surf = pygame.image.frombuffer(buffer, (W, H), "RGB")
        screen.blit(surf, (0, 0))

        fps = clock.get_fps()
        screen.blit(font.render(f"CPU MULTICORE | FPS: {fps:.1f}", True, WHITE), (10, 10))

        pygame.draw.rect(screen, (200, 70, 70), button_rect)
        screen.blit(
            font.render("Switch to GPU", True, WHITE),
            (button_rect.x + 25, button_rect.y + 10)
        )

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
