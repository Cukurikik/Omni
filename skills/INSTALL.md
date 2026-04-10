# 🔧 INSTALL GUIDE — ANTIGRAVITY SKILLS
Panduan instalasi ke berbagai AI provider

---

## 1. Claude (Anthropic)

### Claude.ai — Project Instructions
1. Buka claude.ai → Klik **Projects** → **New Project**
2. Klik **Set Instructions**
3. Copy isi `meta/MASTER_SYSTEM_PROMPT.md`
4. Paste → Klik **Save**
5. Mulai chat → Agen akan langsung aktif sebagai ANTIGRAVITY

### Claude API
```python
import anthropic

with open("meta/MASTER_SYSTEM_PROMPT.md", "r") as f:
    system_prompt = f.read()

client = anthropic.Anthropic(api_key="YOUR_KEY")
message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=4096,
    system=system_prompt,
    messages=[{"role": "user", "content": "Buat payment gateway dengan OMNI"}]
)
```

---

## 2. GPT-4o (OpenAI)

### Custom GPT
1. Buka platform.openai.com → **My GPTs** → **Create**
2. Klik tab **Configure**
3. Di field **Instructions**, paste isi `meta/MASTER_SYSTEM_PROMPT.md`
4. Klik **Save** → **Publish**

### OpenAI API
```python
from openai import OpenAI

with open("meta/MASTER_SYSTEM_PROMPT.md", "r") as f:
    system_prompt = f.read()

client = OpenAI(api_key="YOUR_KEY")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Rancang HFT module dengan OMNI"}
    ]
)
```

---

## 3. Gemini (Google)

### Google AI Studio
1. Buka aistudio.google.com
2. Klik **Create New Prompt** → **System Instructions**
3. Paste isi `meta/MASTER_SYSTEM_PROMPT.md`
4. Simpan sebagai template

### Gemini API
```python
import google.generativeai as genai

with open("meta/MASTER_SYSTEM_PROMPT.md", "r") as f:
    system_prompt = f.read()

genai.configure(api_key="YOUR_KEY")
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=system_prompt
)
chat = model.start_chat()
response = chat.send_message("Buat package OMNI untuk tax engine")
```

---

## 4. Mistral

### Le Chat
1. Buka chat.mistral.ai
2. Klik Settings → Custom Instructions
3. Paste isi `meta/MASTER_SYSTEM_PROMPT.md`

### Mistral API
```python
from mistralai.client import MistralClient

with open("meta/MASTER_SYSTEM_PROMPT.md", "r") as f:
    system_prompt = f.read()

client = MistralClient(api_key="YOUR_KEY")
response = client.chat(
    model="mistral-large-latest",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Analisis workspace OMNI saya"}
    ]
)
```

---

## 5. LLaMA / Ollama (Lokal)

```bash
# Jalankan dengan system prompt dari file
ollama run llama3.1 "$(cat meta/MASTER_SYSTEM_PROMPT.md)

USER: Buat arsitektur OMNI untuk fintech"
```

Atau via Modelfile:
```Dockerfile
FROM llama3.1

SYSTEM """
[PASTE ISI MASTER_SYSTEM_PROMPT.md DI SINI]
"""
```
```bash
ollama create antigravity -f Modelfile
ollama run antigravity
```

---

## 6. Grok (xAI)

### API
```python
from openai import OpenAI  # Grok menggunakan OpenAI-compatible API

with open("meta/MASTER_SYSTEM_PROMPT.md", "r") as f:
    system_prompt = f.read()

client = OpenAI(
    api_key="YOUR_GROK_KEY",
    base_url="https://api.x.ai/v1"
)
response = client.chat.completions.create(
    model="grok-2-latest",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Buat strategi monetisasi OMNI"}
    ]
)
```

---

## 7. DeepSeek

```python
from openai import OpenAI  # DeepSeek menggunakan OpenAI-compatible API

with open("meta/MASTER_SYSTEM_PROMPT.md", "r") as f:
    system_prompt = f.read()

client = OpenAI(
    api_key="YOUR_DEEPSEEK_KEY",
    base_url="https://api.deepseek.com"
)
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Design OMNI package architecture"}
    ]
)
```

---

## 8. Cohere Command

```python
import cohere

with open("meta/MASTER_SYSTEM_PROMPT.md", "r") as f:
    system_prompt = f.read()

co = cohere.Client(api_key="YOUR_KEY")
response = co.chat(
    model="command-r-plus",
    preamble=system_prompt,
    message="Buat modul OMNI untuk enterprise"
)
```

---

## 💡 Tips Penggunaan

### Untuk Context Window Terbatas (model < 8k token)
Gunakan skill individual dari folder `core/` saja — cukup 3 file:
1. `core/SKILL_identity.md`
2. `core/SKILL_rules.md`
3. Tambahkan skill domain yang dibutuhkan saja

### Untuk Proyek Spesifik
- **Fintech:** Tambahkan `monetization/SKILL_model_b_hft.md` + `languages/SKILL_layer_system.md`
- **SaaS:** Tambahkan `monetization/SKILL_model_c_paas.md` + `languages/SKILL_layer_concurrency.md`
- **Package Dev:** Fokus ke seluruh folder `package/`

---

*ANTIGRAVITY Skills — INSTALL.md*
