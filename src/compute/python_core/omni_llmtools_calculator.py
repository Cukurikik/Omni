# Omni LLM-Tools System Requirements Calculator
# Ref: manuelescobar-dev/LLM-Tools — MIT
from typing import Dict

def inference_memory_gb(params_b: float, bits: int = 16, kv_tokens: int = 2048, n_layers: int = 32, hidden: int = 4096, heads: int = 32) -> Dict:
    bpp = bits / 8; model = params_b * 1e9 * bpp / 1e9
    hd = hidden // max(heads, 1); kv = 2 * kv_tokens * heads * hd * bpp * n_layers / 1e9
    return {"model_gb": round(model, 2), "kv_gb": round(kv, 2), "total_gb": round(model + kv + model*0.1, 2)}

def training_memory_gb(params_b: float, bits: int = 16, bs: int = 8, seq: int = 2048) -> Dict:
    bpp = bits / 8; model = params_b * 1e9 * bpp / 1e9; grad = model
    opt = params_b * 1e9 * 8 / 1e9; act = bs * seq * 4096 * 4 / 1e9 * (params_b / 7)
    total = model + grad + opt + act
    return {"total_gb": round(total, 2), "gpus_80gb": max(1, round(total / 70))}

def quant_savings(params_b: float, orig: int = 16, target: int = 4) -> Dict:
    o = params_b * 1e9 * (orig/8) / 1e9; q = params_b * 1e9 * (target/8) / 1e9
    return {"original_gb": round(o,2), "quantized_gb": round(q,2), "ratio": round(orig/target,1)}
