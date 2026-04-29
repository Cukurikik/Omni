# Omni GPT4All Local Inference Engine (Python)
# Ref: Macoron/gpt4all.unity — MIT (+ nomic GPT4All)
from typing import Dict

def load_model_config(model_name: str) -> Dict:
    configs = {
        "gpt4all-j": {"context_length": 2048, "n_params": "6B", "quantization": "q4_0"},
        "orca-mini": {"context_length": 2048, "n_params": "3B", "quantization": "q4_0"},
        "nous-hermes": {"context_length": 4096, "n_params": "13B", "quantization": "q4_1"},
    }
    return configs.get(model_name, {"error": f"Unknown model: {model_name}"})

def estimate_memory(n_params_b: float, quant_bits: int = 4) -> float:
    return round(n_params_b * quant_bits / 8, 2)

def token_count(text: str) -> int: return max(1, len(text) // 4)
