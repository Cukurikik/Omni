# Omni AwesomeAIModels Registry (Python)
# Compute: AI model catalog and comparison.
# Ref: alternbits/awesome-ai-models
from typing import Dict, List

def register_model(registry: Dict, name: str, provider: str, params_b: float, modality: str) -> Dict:
    key = f"{provider}/{name}"
    registry[key] = {"name": name, "provider": provider, "params_b": params_b, "modality": modality}
    return registry

def compare_models(registry: Dict, names: List[str]) -> List[Dict]:
    return sorted([v for k, v in registry.items() if v["name"] in names], key=lambda m: m["params_b"], reverse=True)
