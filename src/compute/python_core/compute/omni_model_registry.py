import os
import json

# ==========================================
# 🧠 PILAR #8: LLM MODEL REGISTRY & SELECTOR
# ==========================================
# omni_llm/ hanya berisi qlora_tuner.py — ini FATAL.
# Agen tidak bisa memanggil model yang tepat tanpa Registri.
# File ini mengelola metadata seluruh model (lokal & cloud) yang tersedia.

class OmniModelRegistry:
    """Registri sentral untuk semua model AI yang dikuasai OMNI."""
    
    def __init__(self):
        self.models = {}
        self._register_defaults()
        print("🗂️ [MODEL-REGISTRY] Pusat Registri Model OMNI Dimuat.")

    def _register_defaults(self):
        self.models = {
            "gemini-2.5-pro": {
                "provider": "google_cloud",
                "type": "cloud_api",
                "cost_per_1k_tokens": 0.00125,
                "max_context": 1_000_000,
                "capabilities": ["reasoning", "code", "vision", "audio"],
            },
            "gemini-2.5-flash": {
                "provider": "google_cloud",
                "type": "cloud_api",
                "cost_per_1k_tokens": 0.00015,
                "max_context": 1_000_000,
                "capabilities": ["reasoning", "code", "fast"],
            },
            "omni-nano-2b": {
                "provider": "local_qlora",
                "type": "on_device",
                "cost_per_1k_tokens": 0.0,
                "max_context": 8192,
                "capabilities": ["code", "fast", "sovereign"],
                "quantization": "GGUF-Q4_K_M",
                "adapter_path": "./omni-lora-checkpoints/",
            },
            "llama-3.1-70b": {
                "provider": "local_vllm",
                "type": "self_hosted",
                "cost_per_1k_tokens": 0.0,
                "max_context": 131072,
                "capabilities": ["reasoning", "code"],
            },
        }

    def register_model(self, model_id: str, metadata: dict):
        self.models[model_id] = metadata
        print(f"   ✅ Model '{model_id}' terdaftar di Registri OMNI.")

    def get_model(self, model_id: str) -> dict:
        if model_id not in self.models:
            raise KeyError(f"❌ Model '{model_id}' tidak ditemukan di Registri!")
        return self.models[model_id]

    def list_sovereign_models(self) -> list:
        """Hanya model yang TIDAK bergantung pada API pihak ketiga."""
        return [k for k, v in self.models.items() if v["type"] != "cloud_api"]

    def select_optimal(self, task_complexity: int, require_sovereign: bool = False) -> str:
        """Pemilihan model otomatis berdasarkan kompleksitas dan kedaulatan."""
        candidates = self.models.items()
        if require_sovereign:
            candidates = [(k, v) for k, v in candidates if v["type"] != "cloud_api"]
        
        if task_complexity > 7:
            return "gemini-2.5-pro" if not require_sovereign else "llama-3.1-70b"
        elif task_complexity > 3:
            return "gemini-2.5-flash" if not require_sovereign else "omni-nano-2b"
        else:
            return "omni-nano-2b"


if __name__ == "__main__":
    registry = OmniModelRegistry()
    
    print(f"\n📋 Model sovereign tersedia: {registry.list_sovereign_models()}")
    
    selected = registry.select_optimal(task_complexity=9, require_sovereign=True)
    print(f"🎯 Model terpilih (sovereign, high complexity): {selected}")
    
    selected2 = registry.select_optimal(task_complexity=2)
    print(f"🎯 Model terpilih (any, low complexity): {selected2}")
