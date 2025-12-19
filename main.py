from menu import choose_shape
from cpu_renderer import run_cpu
from gpu_renderer import run_gpu

shape = choose_shape()
if not shape:
    exit()

cpu_result = run_cpu(shape)

if cpu_result["action"] == "switch":
    gpu_result = run_gpu(shape)
else:
    exit()

print("\n===== FINAL COMPARISON =====")
print(f"Shape: {shape.capitalize()}")

print(f"CPU Avg FPS: {cpu_result['avg_fps']:.2f}")
print(f"CPU Avg ms : {cpu_result['avg_ms']:.2f}")

print(f"GPU Avg FPS: {gpu_result['avg_fps']:.2f}")
print(f"GPU Avg ms : {gpu_result['avg_ms']:.2f}")

print(f"Speedup: {cpu_result['avg_ms'] / gpu_result['avg_ms']:.2f}x")
