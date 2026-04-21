import hashlib
import json
import time

# ==========================================
# 🔀 PILAR #8: INFERENCE ROUTER (LOKAL vs CLOUD)
# ==========================================
# qlora_tuner.py mencetak model, tapi tidak ada yang MEMANGGIL model tsb.
# File ini menjembatani keputusan: pakai model lokal atau cloud?

class OmniInferenceRouter:
    """Router cerdas yang memutuskan apakah inferensi dilayani
    oleh model sovereign lokal atau diteruskan ke Cloud API."""
    
    def __init__(self, registry):
        self.registry = registry
        self.inference_cache = {}
        print("🔀 [INFERENCE-ROUTER] Penjaga Gerbang LLM Pusat Aktif.")

    def _cache_key(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]

    def route_inference(self, prompt: str, complexity: int = 5, 
                        force_sovereign: bool = False) -> dict:
        """Memutuskan jalur inference berdasar kompleksitas dan kebijakan."""
        
        # 1. Cek cache
        key = self._cache_key(prompt)
        if key in self.inference_cache:
            print(f"   ♻️ [CACHE-HIT] Prompt sudah diproses sebelumnya. Cost: $0")
            return self.inference_cache[key]
        
        # 2. Pilih model
        model_id = self.registry.select_optimal(complexity, force_sovereign)
        model_meta = self.registry.get_model(model_id)
        
        print(f"   🔀 [ROUTING] Kompleksitas={complexity} | Sovereign={force_sovereign}")
        print(f"   --> 🧠 Model Terpilih: {model_id} ({model_meta['type']})")
        
        # 3. Dispatch ke engine yang sesuai
        start = time.time()
        if model_meta["type"] == "on_device":
            result = self._invoke_local(model_id, prompt)
        elif model_meta["type"] == "self_hosted":
            result = self._invoke_vllm(model_id, prompt)
        else:
            result = self._invoke_cloud(model_id, prompt)
        
        latency_ms = (time.time() - start) * 1000
        
        response = {
            "model": model_id,
            "type": model_meta["type"],
            "output": result,
            "latency_ms": round(latency_ms, 2),
            "cost_usd": model_meta["cost_per_1k_tokens"] * (len(prompt.split()) / 1000),
        }
        
        self.inference_cache[key] = response
        print(f"   ✅ Respons diterima ({response['latency_ms']}ms, ${response['cost_usd']:.6f})")
        return response

    def _invoke_local(self, model_id: str, prompt: str) -> str:
        """Memanggil model lokal via Ollama API. PRODUCTION."""
        import urllib.request
        import urllib.error
        try:
            url = "http://localhost:11434/api/generate"
            payload = json.dumps({
                "model": model_id.replace("omni-nano-3b", "llama3.2"),
                "prompt": prompt,
                "stream": False,
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "[LOCAL] No response")
        except Exception as e:
            return f"[LOCAL/{model_id}] Ollama error: {e}"

    def _invoke_vllm(self, model_id: str, prompt: str) -> str:
        """Memanggil model self-hosted via vLLM OpenAI-compatible API. PRODUCTION."""
        import urllib.request
        import urllib.error
        try:
            url = "http://localhost:8000/v1/completions"
            payload = json.dumps({
                "model": model_id,
                "prompt": prompt,
                "max_tokens": 512,
                "temperature": 0.7,
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["text"]
        except Exception as e:
            return f"[VLLM/{model_id}] vLLM error: {e}"

    def _invoke_cloud(self, model_id: str, prompt: str) -> str:
        """Memanggil Gemini Cloud API. PRODUCTION."""
        import os
        import urllib.request
        import urllib.error
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return f"[CLOUD/{model_id}] GEMINI_API_KEY belum di-set."
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"[CLOUD/{model_id}] Gemini error: {e}"


if __name__ == "__main__":
    from omni_model_registry import OmniModelRegistry
    
    registry = OmniModelRegistry()
    router = OmniInferenceRouter(registry)
    
    # Uji routing
    router.route_inference("Hitung risiko portofolio sektor energi", complexity=9)
    router.route_inference("Apa ibu kota Indonesia?", complexity=1)
    router.route_inference("Analisis keamanan CIS benchmark", complexity=6, force_sovereign=True)
