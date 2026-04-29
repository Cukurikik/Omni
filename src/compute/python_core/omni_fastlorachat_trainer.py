# Omni FastLoRAChat Trainer
# Ref: bupticybee/FastLoRAChat
from typing import Dict
def compute_lora_config(base_model_params: int, rank: int = 8, alpha: int = 16) -> Dict:
    scaling = alpha / rank
    trainable = 2 * rank * (base_model_params // 1000) * 32
    return {"rank": rank, "alpha": alpha, "scaling": round(scaling, 4), "trainable_params": trainable,
            "ratio": round(trainable / max(base_model_params, 1), 8)}
def estimate_vram(model_params_b: float, batch_size: int, seq_len: int, bits: int = 4) -> float:
    base_gb = model_params_b * bits / 8
    activation_gb = batch_size * seq_len * 4096 * 2 / (1024**3)
    return round(base_gb + activation_gb, 2)
