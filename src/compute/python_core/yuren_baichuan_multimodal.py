import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, Any

class YurenBaichuanEngine:
    """
    Yuren-Baichuan-7B Multimodal Engine for OMNI Framework.
    """
    def __init__(self, model_path: str = "pleisto/yuren-baichuan-7b", device: str = "cuda"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True, torch_dtype=torch.float16).to(self.device)
        self.model.eval()

    def generate_response(self, prompt: str, max_length: int = 512) -> Dict[str, Any]:
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_length=max_length)
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return {"status": "success", "response": response}
        except Exception as e:
            return {"status": "error", "message": str(e), "response": None}
