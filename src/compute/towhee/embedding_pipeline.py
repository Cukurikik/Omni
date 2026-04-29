import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import io
from typing import List, Dict, Any, Union

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error

    @classmethod
    def ok(cls, value: Any):
        return cls(True, value=value)

    @classmethod
    def err(cls, error: str):
        return cls(False, error=error)

class TowheeEmbeddingPipeline:
    def __init__(self, use_gpu: bool = True):
        self.device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
        try:
            self.model = models.resnet50(pretrained=True)
            # Remove the final classification layer to get embeddings
            self.model = torch.nn.Sequential(*(list(self.model.children())[:-1]))
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Towhee pipeline: {e}")

    def process_image(self, image_bytes: bytes) -> OmniResult:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding = self.model(tensor)
                
            embedding = embedding.squeeze().cpu().numpy()
            return OmniResult.ok(embedding.tolist())
        except Exception as e:
            return OmniResult.err(f"Image processing failed: {str(e)}")

    def batch_process(self, batch_bytes: List[bytes]) -> OmniResult:
        try:
            tensors = []
            for img_bytes in batch_bytes:
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                tensors.append(self.transform(img))
                
            batch_tensor = torch.stack(tensors).to(self.device)
            with torch.no_grad():
                embeddings = self.model(batch_tensor)
                
            embeddings = embeddings.squeeze(-1).squeeze(-1).cpu().numpy()
            return OmniResult.ok(embeddings.tolist())
        except Exception as e:
            return OmniResult.err(f"Batch processing failed: {str(e)}")
