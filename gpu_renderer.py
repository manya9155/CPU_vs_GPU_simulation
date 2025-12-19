import pygame
import moderngl
import numpy as np
import time

W, H = 800, 600

def get_shape(shape):
    if shape == "triangle":
        return np.array([
            [-0.2, -0.2],
            [ 0.2, -0.2],
            [ 0.0,  0.2]
        ], dtype="f4")

    if shape == "square":
        return np.array([
            [-0.2, -0.2], [ 0.2, -0.2], [ 0.2,  0.2],
            [-0.2, -0.2], [ 0.2,  0.2], [-0.2,  0.2]
        ], dtype="f4")

    if shape == "rectangle":
        return np.array([
            [-0.3, -0.15], [ 0.3, -0.15], [ 0.3,  0.15],
            [-0.3, -0.15], [ 0.3,  0.15], [-0.3,  0.15]
        ], dtype="f4")

def run_gpu(shape_name):
    pygame.init()
    screen = pygame.display.set_mode(
        (W, H), pygame.OPENGL | pygame.DOUBLEBUF
    )

    ctx = moderngl.create_context()
    ctx.viewport = (0, 0, W, H)

    prog = ctx.program(
        vertex_shader="""
        #version 330
        in vec2 in_vert;
        uniform float angle;
        uniform vec2 offset;
        void main() {
            mat2 r = mat2(cos(angle), -sin(angle),
                          sin(angle),  cos(angle));
            gl_Position = vec4(r * in_vert + offset, 0.0, 1.0);
        }
        """,
        fragment_shader="""
        #version 330
        out vec4 f;
        void main() {
            f = vec4(1.0, 0.3, 0.3, 1.0);
        }
        """
    )

    shape = get_shape(shape_name)
    vbo = ctx.buffer(shape.tobytes())
    vao = ctx.simple_vertex_array(prog, vbo, "in_vert")

    pos = np.array([0.0, 0.0], dtype="f4")
    angle = 0.0

    MOVE = 0.02
    ROT = 0.08

    clock = pygame.time.Clock()
    frame_times = []

    running = True
    while running:
        t0 = time.perf_counter()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  pos[0] -= MOVE
        if keys[pygame.K_RIGHT]: pos[0] += MOVE
        if keys[pygame.K_UP]:    pos[1] += MOVE
        if keys[pygame.K_DOWN]:  pos[1] -= MOVE
        if keys[pygame.K_r]:     angle += ROT

        prog["angle"].value = angle
        prog["offset"].value = tuple(pos)

        ctx.clear()
        vao.render()
        ctx.finish()

        fps = clock.get_fps()
        pygame.display.set_caption(f"GPU MODE | FPS: {fps:.1f}")

        pygame.display.flip()
        clock.tick(60)

        frame_times.append(time.perf_counter() - t0)

    pygame.quit()

    avg_ms = sum(frame_times) / len(frame_times) * 1000
    avg_fps = 1000 / avg_ms

    return {
        "avg_ms": avg_ms,
        "avg_fps": avg_fps
    }
