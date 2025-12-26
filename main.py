# from menu import choose_shape
# from cpu_renderer import run_cpu
# from gpu_renderer import run_gpu

# shape = choose_shape()
# if not shape:
#     exit()

# cpu_result = run_cpu(shape)

# if cpu_result["action"] == "switch":
#     gpu_result = run_gpu(shape)
# else:
#     exit()

# print("\n===== FINAL COMPARISON =====")
# print(f"Shape: {shape.capitalize()}")

# print(f"CPU Avg FPS: {cpu_result['avg_fps']:.2f}")
# print(f"CPU Avg ms : {cpu_result['avg_ms']:.2f}")

# print(f"GPU Avg FPS: {gpu_result['avg_fps']:.2f}")
# print(f"GPU Avg ms : {gpu_result['avg_ms']:.2f}")

# print(f"Speedup: {cpu_result['avg_ms'] / gpu_result['avg_ms']:.2f}x")

if __name__ == "__main__":
    from menu import choose_shape
    from cpu_renderer import run_cpu
    from cpu_renderer_multicore import run_cpu_multicore
    from gpu_renderer import run_gpu
    from cpu_renderer_vectorized import run_cpu_vectorized

    shape = choose_shape()
    if not shape:
        exit()

    # 1️⃣ Single-core CPU
    cpu_single = run_cpu(shape)

    if cpu_single["action"] != "multicore":
        exit()

    # 2️⃣ Multi-core CPU
    cpu_multi = run_cpu_multicore(shape)

    if cpu_multi["action"] != "vec":
        exit()
    
    cpu_vec = run_cpu_vectorized(shape)
    if cpu_vec["action"] != "gpu":
        exit()

    gpu_result = run_gpu(shape)

    # 4️⃣ Final scoreboard
    print("\n===== FINAL PERFORMANCE COMPARISON =====")
    print(f"Shape: {shape.capitalize()}\n")

    print("Single-Core CPU")
    print(f"  Avg FPS : {cpu_single['avg_fps']:.2f}")
    print(f"  Avg ms  : {cpu_single['avg_ms']:.2f}\n")

    print("Multi-Core CPU")
    print(f"  Avg FPS : {cpu_multi['avg_fps']:.2f}")
    print(f"  Avg ms  : {cpu_multi['avg_ms']:.2f}")
    print(f"  Speedup vs Single-Core: {cpu_single['avg_ms'] / cpu_multi['avg_ms']:.2f}x\n")

    print("Vectorized CPU")
    print(f"  Avg FPS : {cpu_vec['avg_fps']:.2f}")
    print(f"  Avg ms  : {cpu_vec['avg_ms']:.2f}")
    print(f"  Speedup vs Single-Core: {cpu_single['avg_ms'] / cpu_vec['avg_ms']:.2f}x")

    print("GPU")
    print(f"  Avg FPS : {gpu_result['avg_fps']:.2f}")
    print(f"  Avg ms  : {gpu_result['avg_ms']:.2f}")
    print(f"  Speedup vs Single-Core: {cpu_single['avg_ms'] / gpu_result['avg_ms']:.2f}x")
    print(f"  Speedup vs Multi-Core : {cpu_multi['avg_ms'] / gpu_result['avg_ms']:.2f}x")
    print(f"  Speedup vs Vectorized : {cpu_vec['avg_ms'] / gpu_result['avg_ms']:.2f}x")
