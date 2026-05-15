import os

def get_resource_usage():
    """Return a dict with current process CPU, RAM, and (if available) GPU usage."""
    data = {
        'cpu_percent': 0.0,
        'ram_mb': 0.0,
        'gpu_percent': None
    }
    
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        data['cpu_percent'] = process.cpu_percent(interval=0.1)
        data['ram_mb'] = mem_info.rss / (1024 * 1024)
    except ImportError:
        pass
    except Exception:
        pass
        
    try:
        import GPUtil # type: ignore
        gpus = GPUtil.getGPUs()
        if gpus:
            data['gpu_percent'] = gpus[0].load * 100
    except ImportError:
        pass
    except Exception:
        pass
        
    return data
