import torch
import torch.nn as nn
from typing import Tuple, Optional

# OMNI MMSEGMENTATION: Dice Loss
# Python PyTorch implementation of Dice Loss, crucial for handling class imbalance in semantic segmentation.
# Source: open-mmlab/mmsegmentation

class SegmentationLossError(Exception):
    pass

class DiceLoss(nn.Module):
    """
    Computes the Dice Loss.
    Loss = 1 - (2 * intersection + smooth) / (prediction_sum + target_sum + smooth)
    """
    def __init__(self, smooth: float = 1e-5):
        super(DiceLoss, self).__init__()
        self.smooth = smooth

    def forward(
        self, 
        predictions: torch.Tensor, 
        targets: torch.Tensor
    ) -> Tuple[Optional[torch.Tensor], Optional[SegmentationLossError]]:
        try:
            # predictions: [batch, classes, height, width] - Assuming logits or probabilities
            # targets: [batch, height, width] or one-hot [batch, classes, height, width]
            
            # Apply sigmoid if predictions are logits (simplification for binary/independent classes)
            probs = torch.sigmoid(predictions)
            
            # Flatten spatial dimensions
            # [batch, classes, height*width]
            probs_flat = probs.view(probs.size(0), probs.size(1), -1)
            
            # If targets are not one-hot, this needs a scatter operation.
            # Assuming targets are one-hot encoded for this structural mock:
            targets_flat = targets.view(targets.size(0), targets.size(1), -1).float()
            
            if probs_flat.shape != targets_flat.shape:
                 return None, SegmentationLossError("Prediction and Target shapes do not match.")

            # Compute intersection: sum over spatial dimension
            intersection = torch.sum(probs_flat * targets_flat, dim=2)
            
            # Compute sums
            probs_sum = torch.sum(probs_flat, dim=2)
            targets_sum = torch.sum(targets_flat, dim=2)
            
            # Dice Coefficient
            dice_coeff = (2.0 * intersection + self.smooth) / (probs_sum + targets_sum + self.smooth)
            
            # Dice Loss = 1 - Dice Coefficient
            # Mean over batch and classes
            dice_loss = 1.0 - dice_coeff.mean()
            
            return dice_loss, None
            
        except Exception as e:
            return None, SegmentationLossError(f"Dice Loss computation failed: {str(e)}")
