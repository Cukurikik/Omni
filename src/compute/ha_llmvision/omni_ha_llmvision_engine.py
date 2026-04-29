from typing import Dict, Any
from dataclasses import dataclass
import base64, hashlib

# OMNI HA-LLMVision Engine — Compute Layer
# Absorbing valentinfrlch/ha-llmvision: Visual intelligence for Home Assistant.
# Production image analysis request builder with multi-provider support.

@dataclass
class HaVisionResult:
    ok: bool
    request_payload: Dict = None
    error: str = None

class OmniHaLlmVisionEngine:
    PROVIDERS = {"openai", "anthropic", "google", "ollama", "localai"}

    def __init__(self):
        self.analyses = 0

    def build_analysis_request(self, image_bytes: bytes, prompt: str,
                                provider: str = "openai", max_tokens: int = 300) -> HaVisionResult:
        if not image_bytes:
            return HaVisionResult(False, error="HaVisionError: Empty image")
        if not prompt:
            return HaVisionResult(False, error="HaVisionError: Prompt required")
        if provider not in self.PROVIDERS:
            return HaVisionResult(False, error=f"HaVisionError: Unknown provider '{provider}'")
        self.analyses += 1
        b64 = base64.b64encode(image_bytes).decode("ascii")
        img_hash = hashlib.sha256(image_bytes).hexdigest()[:16]
        payload = {
            "provider": provider,
            "prompt": prompt,
            "image_b64": b64,
            "image_hash": img_hash,
            "max_tokens": max_tokens,
            "size_bytes": len(image_bytes)
        }
        return HaVisionResult(True, request_payload=payload)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniHaLlmVisionEngine", "analyses": self.analyses,
                "providers": list(self.PROVIDERS), "status": "Operational"}
