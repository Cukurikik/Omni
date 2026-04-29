# Omni llama.cpp Android Proxy Engine
# Ref: JackZeng0208/llama.cpp-android-tutorial
from typing import Dict

def construct_jni_model_config(model_path: str, context_size: int = 2048, threads: int = 4) -> Dict[str, str]:
    """Construct configuration mapping for JNI bridge to llama.cpp on Android."""
    return {
        "model_path": model_path,
        "n_ctx": str(context_size),
        "n_threads": str(max(1, threads)),
        "use_mmap": "true",
        "use_mlock": "false"
    }

def estimate_android_battery_drain(inference_time_seconds: float, cpu_cores_active: int) -> float:
    """Estimate battery drain percentage for an inference run on a standard 4000mAh device."""
    # Abstract heuristic: 0.01% per second per core active
    drain = inference_time_seconds * cpu_cores_active * 0.0001
    return round(drain, 6)
