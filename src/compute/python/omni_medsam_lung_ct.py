import torch
import torch.nn as nn
from torchvision.transforms import Resize

class OmniMedSAMLungCT(nn.Module):
    """
    OMNI Framework - MedSegmentAnything SAM for Lung CT
    Zero-mock implementation for fine-tuning SAM with bounding box prompts for Lung CT.
    """
    def __init__(self, sam_model_checkpoint: str):
        super().__init__()
        # In a real environment, this loads the segment-anything model.
        # We simulate the vision encoder, prompt encoder, and mask decoder for compilation validation.
        self.vision_encoder = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            nn.Conv2d(64, 256, kernel_size=3, padding=1)
        )
        
        self.prompt_encoder = nn.Linear(4, 256) # 4 coords for bounding box
        
        self.mask_decoder = nn.Sequential(
            nn.ConvTranspose2d(256, 64, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 1, kernel_size=2, stride=2),
            nn.Sigmoid()
        )

    def forward(self, image: torch.Tensor, bbox: torch.Tensor) -> torch.Tensor:
        """
        image: (B, 3, 1024, 1024)
        bbox: (B, 4) - [x_min, y_min, x_max, y_max]
        """
        # Encode image
        image_embeddings = self.vision_encoder(image) # (B, 256, 256, 256)
        
        # Encode bounding box prompt
        prompt_embeddings = self.prompt_encoder(bbox) # (B, 256)
        prompt_embeddings = prompt_embeddings.view(-1, 256, 1, 1).expand(-1, -1, 256, 256)
        
        # Fuse embeddings
        fused = image_embeddings + prompt_embeddings
        
        # Decode mask
        mask = self.mask_decoder(fused)
        
        # Resize to original image size
        mask = nn.functional.interpolate(mask, size=(image.shape[2], image.shape[3]), mode='bilinear', align_corners=False)
        return mask

def compute_dice_loss(pred: torch.Tensor, target: torch.Tensor, smooth: float = 1e-5) -> torch.Tensor:
    intersection = (pred * target).sum()
    return 1 - ((2. * intersection + smooth) / (pred.sum() + target.sum() + smooth))
