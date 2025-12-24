import pygame
import moderngl
import numpy as np
import time
import math

W, H = 800, 600

# ================= SHAPES =================
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

# ================= GPU PIPELINE =================
def run_gpu(shape_name):
    pygame.init()
    pygame.display.set_mode(
        (W, H), pygame.OPENGL | pygame.DOUBLEBUF
    )

    ctx = moderngl.create_context()
    ctx.viewport = (0, 0, W, H)

    # ===== SHADERS =====
    prog = ctx.program(
        vertex_shader="""
        #version 330
        in vec2 in_vert;
        in vec3 in_color;

        uniform float angle;
        uniform vec2 offset;

        out vec3 v_color;

        void main() {
            mat2 r = mat2(
                cos(angle), -sin(angle),
                sin(angle),  cos(angle)
            );
            gl_Position = vec4(r * in_vert + offset, 0.0, 1.0);
            v_color = in_color;
        }
        """,
        fragment_shader="""
        #version 330
        in vec3 v_color;
        out vec4 f;

        void main() {
            f = vec4(v_color, 1.0);
        }
        """
    )

    # ===== GEOMETRY =====
    shape = get_shape(shape_name)

    # CPU-equivalent vertex colors
    VERTEX_COLORS = np.array([
        [1.0, 0.0, 0.0],  # red
        [0.0, 1.0, 0.0],  # green
        [0.0, 0.0, 1.0],  # blue
    ], dtype="f4")

    colors = np.tile(VERTEX_COLORS, (len(shape) // 3, 1))

    # Interleave position + color
    vbo = ctx.buffer(np.hstack([shape, colors]).tobytes())
    vao = ctx.simple_vertex_array(
        prog, vbo,
        "in_vert", "in_color"
    )

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

        ctx.clear(0.1, 0.1, 0.1)
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
