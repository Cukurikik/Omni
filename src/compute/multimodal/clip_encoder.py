import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from typing import List, Dict, Any, Union
import io

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class MultimodalCLIPEncoder:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", use_gpu: bool = True):
        self.device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        try:
            self.model = CLIPModel.from_pretrained(model_name).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.model.eval()
        except Exception as e:
            raise RuntimeError(f"Failed to load CLIP model: {e}")

    def encode_text(self, texts: List[str]) -> OmniResult:
        try:
            inputs = self.processor(text=texts, return_tensors="pt", padding=True, truncation=True).to(self.device)
            with torch.no_grad():
                embeddings = self.model.get_text_features(**inputs)
            
            embeddings = embeddings / embeddings.norm(p=2, dim=-1, keepdim=True)
            return OmniResult.ok(embeddings.cpu().numpy().tolist())
        except Exception as e:
            return OmniResult.err(f"Text encoding failed: {str(e)}")

    def encode_image(self, image_bytes_list: List[bytes]) -> OmniResult:
        try:
            images = [Image.open(io.BytesIO(b)).convert("RGB") for b in image_bytes_list]
            inputs = self.processor(images=images, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                embeddings = self.model.get_image_features(**inputs)
                
            embeddings = embeddings / embeddings.norm(p=2, dim=-1, keepdim=True)
            return OmniResult.ok(embeddings.cpu().numpy().tolist())
        except Exception as e:
            return OmniResult.err(f"Image encoding failed: {str(e)}")
