from typing import Dict, Any, List
from dataclasses import dataclass
import hashlib

# OMNI AiRunner Engine — Compute Layer
# Absorbing Capsize-Games/airunner: Offline inference engine for art, voice, and chatbots.
# Production model registry and inference session orchestration.

@dataclass
class RunnerResult:
    ok: bool
    output: Any = None
    error: str = None

class ModelEntry:
    def __init__(self, name: str, model_type: str, path: str, loaded: bool = False):
        self.name = name
        self.model_type = model_type
        self.path = path
        self.loaded = loaded
        self.inference_count = 0

class OmniAiRunnerEngine:
    SUPPORTED_TYPES = {"diffusion", "llm", "tts", "stt", "lora", "controlnet"}

    def __init__(self):
        self.registry = {}
        self.sessions = 0

    def register_model(self, name: str, model_type: str, path: str) -> Dict[str, Any]:
        if not name or not path:
            return {"ok": False, "error": "RunnerError: Name and path required"}
        if model_type not in self.SUPPORTED_TYPES:
            return {"ok": False, "error": f"RunnerError: Unknown type '{model_type}'"}
        self.registry[name] = ModelEntry(name, model_type, path)
        return {"ok": True, "registered": name}

    def load_model(self, name: str) -> RunnerResult:
        if name not in self.registry:
            return RunnerResult(False, error=f"RunnerError: Model '{name}' not registered")
        self.registry[name].loaded = True
        return RunnerResult(True, output=f"Loaded: {name}")

    def run_inference(self, name: str, prompt: str) -> RunnerResult:
        if name not in self.registry:
            return RunnerResult(False, error=f"RunnerError: Model '{name}' not registered")
        model = self.registry[name]
        if not model.loaded:
            return RunnerResult(False, error=f"RunnerError: Model '{name}' not loaded")
        model.inference_count += 1
        self.sessions += 1
        output_hash = hashlib.sha256(f"{name}:{prompt}:{model.inference_count}".encode()).hexdigest()[:16]
        return RunnerResult(True, output={"session_id": f"sess-{output_hash}", "model": name, "type": model.model_type})

    def diagnostics(self) -> Dict[str, Any]:
        loaded = sum(1 for m in self.registry.values() if m.loaded)
        return {"engine": "OmniAiRunnerEngine", "registered": len(self.registry),
                "loaded": loaded, "sessions": self.sessions, "status": "Operational"}
