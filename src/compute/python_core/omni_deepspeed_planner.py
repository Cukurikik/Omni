# Omni DeepSpeed ZeRO Optimizer Planner
# Ref: bobo0810/LearnDeepSpeed — MIT
from typing import Dict
def zero_memory_estimate(model_params_m: float, stage: int, n_gpus: int) -> Dict:
    bytes_per_param = 4; total_bytes = model_params_m * 1e6 * bytes_per_param
    if stage == 1: per_gpu = total_bytes / n_gpus + total_bytes * 8 / n_gpus
    elif stage == 2: per_gpu = total_bytes / n_gpus + total_bytes * 4 / n_gpus
    elif stage == 3: per_gpu = total_bytes * 16 / n_gpus
    else: per_gpu = total_bytes * 16
    return {"stage": stage, "per_gpu_gb": round(per_gpu / 1e9, 2), "total_gb": round(total_bytes*16/1e9, 2)}
def optimal_stage(model_params_m: float, gpu_memory_gb: float, n_gpus: int) -> int:
    for stage in [1, 2, 3]:
        est = zero_memory_estimate(model_params_m, stage, n_gpus)
        if est["per_gpu_gb"] < gpu_memory_gb * 0.85: return stage
    return 3
def gradient_accumulation_steps(batch_size: int, micro_batch: int, n_gpus: int) -> int:
    return max(1, batch_size // (micro_batch * n_gpus))
