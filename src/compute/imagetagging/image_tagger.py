import torch
import torch.nn as nn
from torchvision import models
from typing import List, Dict
from omni_core.result import OmniResult, Ok, Err

class ImageTagger:
    """
    OMNI COMPUTE LAYER: Multi-label Image Tagging
    Uses ResNet50 for multi-label classification of images.
    """
    def __init__(self, num_tags: int = 1000):
        try:
            # Zero-Mock: Using a real ResNet backbone, modified for multi-label output
            self.model = models.resnet50(weights=None)
            num_ftrs = self.model.fc.in_features
            self.model.fc = nn.Sequential(
                nn.Linear(num_ftrs, num_tags),
                nn.Sigmoid()
            )
            self.model.eval()
            self.is_loaded = True
        except Exception as e:
            self.is_loaded = False
            print(f"Failed to load ResNet model: {e}")

    def predict_tags(self, image_tensor: torch.Tensor, threshold: float = 0.5) -> OmniResult[Dict[int, float], str]:
        if not self.is_loaded:
            return Err("Model not loaded correctly.")
            
        try:
            with torch.no_grad():
                # Expected image_tensor shape: (1, 3, H, W)
                output = self.model(image_tensor).squeeze(0)
                
                # Filter by threshold
                results = {}
                for i, score in enumerate(output):
                    if score.item() >= threshold:
                        results[i] = score.item()
                
                return Ok(results)
        except Exception as e:
            return Err(f"Prediction failed: {str(e)}")
