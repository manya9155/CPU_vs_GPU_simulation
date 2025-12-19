import pygame
import numpy as np
import time
import math

W, H = 800, 600
WHITE = (255, 255, 255)
RED = (220, 60, 60)

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

def run_cpu(shape_name):
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("CPU MODE")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    verts = get_shape(shape_name)
    pos = np.array([W // 2, H // 2], dtype=float)
    angle = 0.0

    MOVE = 4
    ROT = 0.08

    frame_times = []

    # --- Switch button ---
    button_rect = pygame.Rect(W - 210, H - 60, 190, 40)

    running = True
    switch_to_gpu = False

    while running:
        t0 = time.perf_counter()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
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

        screen.fill((30, 30, 30))

        for i in range(0, len(transformed), 3):
            pygame.draw.polygon(screen, RED, transformed[i:i+3])

        # --- FPS ---
        fps = clock.get_fps()
        txt = font.render(f"CPU MODE | FPS: {fps:.1f}", True, WHITE)
        screen.blit(txt, (10, 10))

        # --- Button ---
        pygame.draw.rect(screen, (70, 70, 200), button_rect)
        label = font.render("Switch to GPU", True, WHITE)
        screen.blit(label, (button_rect.x + 20, button_rect.y + 10))

        pygame.display.flip()
        clock.tick(60)

        frame_times.append(time.perf_counter() - t0)

    pygame.quit()

    avg_ms = sum(frame_times) / len(frame_times) * 1000
    avg_fps = 1000 / avg_ms

    if switch_to_gpu:
        return {
            "action": "switch",
            "avg_ms": avg_ms,
            "avg_fps": avg_fps
        }

    return {
        "action": "exit",
        "avg_ms": avg_ms,
        "avg_fps": avg_fps
    }


    avg_ms = sum(frame_times) / len(frame_times) * 1000
    avg_fps = 1000 / avg_ms

    return {
        "avg_ms": avg_ms,
        "avg_fps": avg_fps
    }
