import math
import time
import random

# ==========================================
# 🧠 OMNI LOCAL LLM: Inference Engine (Phase 156)
# ==========================================
# Covers: llama.cpp internals, Ollama model management, LM Studio
#
# PROSES BELAJAR JUJUR:
# ──────────────────────
# llama.cpp adalah FONDASI yang dipakai Ollama dan LM Studio.
# Untuk benar-benar memahami tool-tool ini, saya HARUS memahami
# bagaimana inference LLM sebenarnya bekerja:
#
# 1. TOKENIZATION — teks → tokens (integers)
# 2. PREFILL — seluruh prompt diproses sekaligus (compute-bound)
# 3. KV CACHE — simpan Key/Value vectors untuk re-use
# 4. DECODE — generate token satu per satu (memory-bandwidth-bound)
# 5. SAMPLING — logits → probabilitas → pilih token
# 6. DETOKENIZATION — tokens → teks
#
# Ollama = Go server yang wraps llama.cpp + model management (pull/serve)
# LM Studio = Desktop GUI yang wraps llama.cpp + model discovery

# ─────────────────────────────────────────────────
# KOMPONEN 1: Tokenizer (BPE Sederhana)
# ─────────────────────────────────────────────────
class SimpleTokenizer:
    """BPE-style tokenizer (simplified)."""

    def __init__(self):
        # Vocabulary simulasi (dalam realita, tokenizer punya 32K+ tokens)
        self.vocab = {
            "<s>": 0, "</s>": 1, "<pad>": 2,
            "Halo": 3, "saya": 4, "adalah": 5, "AI": 6,
            "asisten": 7, "Omni": 8, "Framework": 9,
            "Yang": 10, "bisa": 11, "membantu": 12, "Anda": 13,
            "dengan": 14, "tugas": 15, "apapun": 16,
            "multi": 17, "agent": 18, "system": 19,
            ".": 20, ",": 21, "!": 22, "?": 23,
        }
        self.id_to_token = {v: k for k, v in self.vocab.items()}

    def encode(self, text):
        tokens = [self.vocab.get("<s>")]
        for word in text.split():
            token_id = self.vocab.get(word, random.randint(3, 23))
            tokens.append(token_id)
        return tokens

    def decode(self, token_ids):
        words = []
        for tid in token_ids:
            if tid in (0, 1, 2):
                continue
            words.append(self.id_to_token.get(tid, f"<unk:{tid}>"))
        return " ".join(words)


# ─────────────────────────────────────────────────
# KOMPONEN 2: KV Cache (Short-Term Memory)
# ─────────────────────────────────────────────────
class KVCache:
    """
    PELAJARAN KUNCI:
    KV Cache = "short-term memory" dari model.
    Setiap token yang diproses menghasilkan Key dan Value vectors.
    TANPA cache: setiap token baru harus re-compute K,V untuk
    SEMUA token sebelumnya → O(n²) waktu.
    DENGAN cache: hanya compute K,V untuk token BARU → O(n) amortized.

    Masalah utama: KV cache BISA SANGAT BESAR.
    Solusi: quantize KV cache (Q8_0) untuk hemat VRAM.
    """

    def __init__(self, n_layers, n_heads, head_dim, max_seq_len=2048):
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.head_dim = head_dim
        self.max_seq_len = max_seq_len
        self.seq_len = 0  # Current position

        # Cache storage: [layer][head][position][dim]
        self.k_cache = [[[] for _ in range(n_heads)] for _ in range(n_layers)]
        self.v_cache = [[[] for _ in range(n_heads)] for _ in range(n_layers)]

    def append(self, layer, head, k_vec, v_vec):
        """Tambah K,V vectors untuk posisi baru."""
        self.k_cache[layer][head].append(k_vec)
        self.v_cache[layer][head].append(v_vec)

    def get_kv(self, layer, head):
        """Ambil semua cached K,V untuk attention computation."""
        return self.k_cache[layer][head], self.v_cache[layer][head]

    def memory_usage_bytes(self):
        """Estimasi VRAM usage (FP16 = 2 bytes per value)."""
        n_values = self.seq_len * self.n_layers * self.n_heads * self.head_dim * 2
        return n_values * 2  # FP16

    def memory_usage_q8_bytes(self):
        """Jika KV cache di-quantize ke Q8_0 → hemat 50%."""
        return self.memory_usage_bytes() // 2


# ─────────────────────────────────────────────────
# KOMPONEN 3: Sampling (Logits → Token)
# ─────────────────────────────────────────────────
class Sampler:
    """
    PELAJARAN:
    Setelah model menghasilkan logits (raw scores),
    sampling mengubahnya menjadi 1 token yang dipilih.

    Techniques:
    - Temperature: kontrol randomness (0=greedy, 1=normal, >1=creative)
    - Top-K: hanya pertimbangkan K token teratas
    - Top-P (nucleus): pertimbangkan token sampai cumulative prob >= P
    """

    @staticmethod
    def softmax(logits):
        max_logit = max(logits)
        exps = [math.exp(l - max_logit) for l in logits]
        total = sum(exps)
        return [e / total for e in exps]

    @staticmethod
    def apply_temperature(logits, temperature=1.0):
        if temperature == 0:
            return logits
        return [l / temperature for l in logits]

    @staticmethod
    def top_k_filter(probs, k=10):
        indexed = list(enumerate(probs))
        indexed.sort(key=lambda x: x[1], reverse=True)
        top_k = indexed[:k]
        total = sum(p for _, p in top_k)
        return [(idx, p / total) for idx, p in top_k]

    @staticmethod
    def top_p_filter(probs, p=0.9):
        indexed = list(enumerate(probs))
        indexed.sort(key=lambda x: x[1], reverse=True)
        cumulative = 0
        filtered = []
        for idx, prob in indexed:
            cumulative += prob
            filtered.append((idx, prob))
            if cumulative >= p:
                break
        total = sum(pr for _, pr in filtered)
        return [(idx, pr / total) for idx, pr in filtered]

    def sample(self, logits, temperature=0.7, top_k=10, top_p=0.9):
        """Full sampling pipeline."""
        # 1. Apply temperature
        scaled = self.apply_temperature(logits, temperature)
        # 2. Softmax
        probs = self.softmax(scaled)
        # 3. Top-K filtering
        filtered = self.top_k_filter(probs, top_k)
        # 4. Top-P filtering
        final = self.top_p_filter([p for _, p in filtered], top_p)
        # Map back to original indices
        final_mapped = [(filtered[i][0], p) for i, (_, p) in enumerate(final) if i < len(filtered)]
        # 5. Weighted random selection
        r = random.random()
        cumulative = 0
        for idx, prob in final_mapped:
            cumulative += prob
            if r <= cumulative:
                return idx, prob
        return final_mapped[-1] if final_mapped else (0, 0.0)


# ─────────────────────────────────────────────────
# KOMPONEN 4: LLM Inference Engine (llama.cpp style)
# ─────────────────────────────────────────────────
class LlamaInferenceEngine:
    """
    llama.cpp-style inference engine.
    Meniru 2 fase utama:
    1. PREFILL: proses seluruh prompt (parallel, compute-bound)
    2. DECODE: generate token satu per satu (sequential, memory-bound)
    """

    def __init__(self, vocab_size=24, n_layers=4, n_heads=4, head_dim=8):
        self.vocab_size = vocab_size
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.head_dim = head_dim
        self.tokenizer = SimpleTokenizer()
        self.sampler = Sampler()
        self.kv_cache = None

        print(f"🧠 [LLAMA.CPP] Engine diinisiasi:")
        print(f"   Vocab: {vocab_size} | Layers: {n_layers} | Heads: {n_heads} | Dim: {head_dim}")

    def _simulate_prefill(self, tokens):
        """
        PREFILL STAGE:
        Seluruh prompt sequence diproses SEKALIGUS (parallel).
        Ini COMPUTE-BOUND (banyak matrix multiply besar).
        Output: KV cache terisi untuk semua token prompt.
        """
        self.kv_cache = KVCache(self.n_layers, self.n_heads, self.head_dim)
        t0 = time.time()

        for pos, token in enumerate(tokens):
            for layer in range(self.n_layers):
                for head in range(self.n_heads):
                    # Generate K,V vectors (dalam realita = weight × input)
                    k = [random.gauss(0, 0.1) for _ in range(self.head_dim)]
                    v = [random.gauss(0, 0.1) for _ in range(self.head_dim)]
                    self.kv_cache.append(layer, head, k, v)
            self.kv_cache.seq_len = pos + 1

        elapsed = (time.time() - t0) * 1000
        print(f"   ⚡ PREFILL: {len(tokens)} tokens, {elapsed:.1f}ms")
        print(f"      KV Cache: {self.kv_cache.seq_len} positions filled")
        print(f"      (Compute-bound: semua tokens diproses parallel)")

    def _simulate_decode_step(self):
        """
        DECODE STAGE (single step):
        Generate 1 token. MEMORY-BANDWIDTH BOUND karena harus
        membaca seluruh model weights + KV cache untuk 1 token saja.
        """
        # Simulasi logits generation
        logits = [random.gauss(0, 2.0) for _ in range(self.vocab_size)]

        # Boost beberapa token yang masuk akal
        logits[6] += 3.0   # "AI"
        logits[8] += 2.5   # "Omni"
        logits[12] += 2.0  # "membantu"
        logits[13] += 1.5  # "Anda"
        logits[20] += 1.0  # "."

        # Sample
        token_id, prob = self.sampler.sample(logits, temperature=0.7, top_k=10, top_p=0.9)

        # Update KV cache
        for layer in range(self.n_layers):
            for head in range(self.n_heads):
                k = [random.gauss(0, 0.1) for _ in range(self.head_dim)]
                v = [random.gauss(0, 0.1) for _ in range(self.head_dim)]
                self.kv_cache.append(layer, head, k, v)
        self.kv_cache.seq_len += 1

        return token_id, prob

    def generate(self, prompt, max_new_tokens=10):
        """Full generation pipeline."""
        print(f"\n   📝 Prompt: \"{prompt}\"")

        # Tokenize
        tokens = self.tokenizer.encode(prompt)
        print(f"   🔤 Tokens: {tokens} ({len(tokens)} tokens)")

        # Phase 1: PREFILL
        self._simulate_prefill(tokens)

        # Phase 2: DECODE (autoregressive)
        print(f"   🔄 DECODE: generating {max_new_tokens} tokens (autoregressive)...")
        generated = []
        for i in range(max_new_tokens):
            token_id, prob = self._simulate_decode_step()
            token_text = self.tokenizer.id_to_token.get(token_id, f"<{token_id}>")
            generated.append(token_id)
            print(f"      [{i+1}] token={token_id} ('{token_text}') prob={prob:.3f} | KV pos={self.kv_cache.seq_len}")

            if token_id == 1:  # EOS
                break

        # Detokenize
        output_text = self.tokenizer.decode(generated)
        return output_text


# ─────────────────────────────────────────────────
# KOMPONEN 5: Ollama Model Manager
# ─────────────────────────────────────────────────
class OllamaModelManager:
    """
    PELAJARAN: Ollama = Go server wrapping llama.cpp.
    - Client-Server architecture (REST API on :11434)
    - Model management mirip Docker (pull, create, delete)
    - Modelfile = Dockerfile untuk model (FROM, SYSTEM, PARAMETER)
    - Dynamic lifecycle: load/unload model sesuai kebutuhan
    - OpenAI-compatible API (/v1/chat/completions)
    """

    def __init__(self):
        self.models = {}
        self.loaded_model = None
        self.api_port = 11434
        print(f"🦙 [OLLAMA] Server diinisiasi (port {self.api_port})")

    def pull(self, model_name: str, size_gb: float = 4.7):
        """ollama pull — download model dari registry."""
        print(f"   📥 [PULL] {model_name} ({size_gb:.1f}GB)...")
        self.models[model_name] = {
            "name": model_name,
            "size_gb": size_gb,
            "family": model_name.split(":")[0] if ":" in model_name else model_name,
            "quantization": "Q4_K_M",
            "status": "downloaded",
            "parameters": {},
        }
        print(f"      ✅ Model {model_name} downloaded ({size_gb:.1f}GB)")

    def create_from_modelfile(self, name: str, modelfile: dict):
        """
        ollama create — buat custom model dari Modelfile.
        PELAJARAN: Modelfile directives:
          FROM: base model
          SYSTEM: system prompt (persona)
          PARAMETER: temperature, top_k, num_ctx
          TEMPLATE: prompt format template
          ADAPTER: LoRA adapter path
        """
        base = modelfile.get("FROM", "llama3.2")
        print(f"   📝 [CREATE] '{name}' dari Modelfile:")
        print(f"      FROM: {base}")
        print(f"      SYSTEM: {modelfile.get('SYSTEM', 'N/A')[:50]}...")
        for param, val in modelfile.get("PARAMETER", {}).items():
            print(f"      PARAMETER {param}: {val}")

        self.models[name] = {
            "name": name,
            "base": base,
            "system": modelfile.get("SYSTEM", ""),
            "parameters": modelfile.get("PARAMETER", {}),
            "status": "created",
        }
        print(f"      ✅ Custom model '{name}' created!")

    def load(self, model_name: str):
        """Load model ke memory (GPU/RAM)."""
        if model_name not in self.models:
            print(f"   ❌ Model '{model_name}' not found! Use 'pull' first.")
            return
        self.loaded_model = model_name
        self.models[model_name]["status"] = "loaded"
        print(f"   🚀 [LOAD] {model_name} loaded into memory")

    def api_chat(self, messages: list, stream: bool = True):
        """
        /api/chat endpoint — OpenAI-compatible.
        PELAJARAN: Ollama exposes /v1/chat/completions
        sehingga bisa jadi drop-in replacement untuk OpenAI API.
        """
        if not self.loaded_model:
            return {"error": "No model loaded"}

        model = self.models[self.loaded_model]
        user_msg = messages[-1].get("content", "") if messages else ""
        print(f"   💬 [CHAT] model={self.loaded_model}")
        print(f"      User: {user_msg[:50]}...")

        # Simulate streaming response
        response_tokens = ["Saya", "adalah", "Omni", "AI", "asisten", "."]
        full_response = ""
        if stream:
            print(f"      Stream: ", end="")
            for token in response_tokens:
                full_response += token + " "
                print(token, end=" ", flush=True)
                time.sleep(0.05)
            print()
        else:
            full_response = " ".join(response_tokens)

        return {
            "model": self.loaded_model,
            "message": {"role": "assistant", "content": full_response.strip()},
            "done": True,
        }

    def list_models(self):
        print(f"   📋 Installed models:")
        for name, info in self.models.items():
            print(f"      {name}: {info.get('size_gb', '?')}GB, status={info['status']}")


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("🧠 OMNI INFERENCE — llama.cpp + Ollama + LM Studio Internals")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   llama.cpp = C++ inference engine:")
    print("     1. Tokenize → 2. Prefill (parallel, compute-bound)")
    print("     → 3. KV Cache → 4. Decode (sequential, memory-bound)")
    print("     → 5. Sample (temp/top-k/top-p) → 6. Detokenize")
    print("   Ollama = Go server yang wraps llama.cpp + model management.")
    print("   LM Studio = Desktop GUI yang wraps llama.cpp + model discovery.")

    # ── PART 1: llama.cpp inference ──
    print(f"\n{'─'*60}")
    print("📋 PART 1: llama.cpp Inference Engine")
    engine = LlamaInferenceEngine(vocab_size=24, n_layers=4, n_heads=4, head_dim=8)
    output = engine.generate("Halo saya adalah Omni", max_new_tokens=6)
    print(f"\n   🎯 Generated: \"{output}\"")
    print(f"   💾 KV Cache VRAM: {engine.kv_cache.memory_usage_bytes():,} bytes (FP16)")
    print(f"   💾 KV Cache Q8:   {engine.kv_cache.memory_usage_q8_bytes():,} bytes (quantized, 50% hemat)")

    # ── PART 2: Ollama Model Manager ──
    print(f"\n{'─'*60}")
    print("📋 PART 2: Ollama Server + Model Management")
    ollama = OllamaModelManager()

    # Pull models
    ollama.pull("qwen3:8b", 4.7)
    ollama.pull("llama4:13b", 7.4)

    # Create custom model via Modelfile
    ollama.create_from_modelfile("omni-assistant", {
        "FROM": "qwen3:8b",
        "SYSTEM": "Kamu adalah Omni AI, asisten cerdas buatan Indonesia.",
        "PARAMETER": {"temperature": 0.7, "top_k": 40, "num_ctx": 4096},
    })

    # Load & Chat
    ollama.load("omni-assistant")
    ollama.list_models()
    result = ollama.api_chat([
        {"role": "system", "content": "Kamu adalah asisten AI."},
        {"role": "user", "content": "Jelaskan apa itu multi-agent system?"},
    ], stream=True)

    print(f"\n{'='*70}")
    print("✅ Inference Engine: DIPELAJARI MENDALAM.")
    print("   Tokenizer (BPE encode/decode) ✓")
    print("   Prefill (parallel, compute-bound) ✓")
    print("   KV Cache (short-term memory + quantization) ✓")
    print("   Decode (autoregressive, memory-bandwidth-bound) ✓")
    print("   Sampling (temperature + top-k + top-p pipeline) ✓")
    print("   Ollama (pull + Modelfile + load + /api/chat) ✓")
    print(f"{'='*70}")
