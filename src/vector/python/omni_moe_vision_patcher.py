import torch

class OmniMoEVisionPatcher:
    """
    OMNI Framework - Vision Patcher for MoE-LLaVA
    Splits high-resolution images into localized patches. These patches are then
    embedded and routed to specific vision experts (e.g., OCR expert, Nature expert)
    by the MoE-LLaVA encoder (File 25).
    """
    def __init__(self, patch_size: int = 14, image_size: int = 224):
        self.patch_size = patch_size
        self.image_size = image_size
        self.num_patches = (image_size // patch_size) ** 2
        print(f"OMNI Python: Vision Patcher initialized. Image will be split into {self.num_patches} patches.")

    def extract_patches(self, images: torch.Tensor) -> torch.Tensor:
        """
        images: [Batch, Channels, Height, Width]
        Returns: [Batch, Num_Patches, Channels * Patch_Size * Patch_Size]
        """
        B, C, H, W = images.shape
        assert H == self.image_size and W == self.image_size, "Image size mismatch"
        
        # Unfold the image into patches
        # [B, C, H//p, p, W//p, p]
        patches = images.unfold(2, self.patch_size, self.patch_size).unfold(3, self.patch_size, self.patch_size)
        
        # Rearrange to [B, num_patches, C*p*p]
        patches = patches.contiguous().view(B, C, -1, self.patch_size, self.patch_size)
        patches = patches.permute(0, 2, 1, 3, 4).contiguous()
        patches = patches.view(B, self.num_patches, -1)
        
        return patches

# Usage
# patcher = OmniMoEVisionPatcher()
# dummy_img = torch.randn(1, 3, 224, 224)
# out = patcher.extract_patches(dummy_img)
# print(f"Patches shape: {out.shape}") # Expected: [1, 256, 3*14*14]
