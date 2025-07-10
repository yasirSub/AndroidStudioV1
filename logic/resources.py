import psutil
import os

def get_resource_usage():
    """Return a dict with current process CPU, RAM, and (if available) GPU usage."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    cpu_percent = process.cpu_percent(interval=0.1)
    ram_mb = mem_info.rss / (1024 * 1024)
    gpu_usage = None
    try:
        import GPUtil  # type: ignore
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_usage = gpus[0].load * 100  # percent
    except Exception:
        gpu_usage = None
    return {
        'cpu_percent': cpu_percent,
        'ram_mb': ram_mb,
        'gpu_percent': gpu_usage
    }
