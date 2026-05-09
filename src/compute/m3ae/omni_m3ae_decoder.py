"""
omni_m3ae_decoder.py — M3AE Multimodal Decoder
Inspired by: M3AE (Multimodal Masked Autoencoders)
Layer: Compute / AI

Transformer decoder responsible for reconstructing both text tokens and 
image patches from the fused latent representations.
"""

import torch
import torch.nn as nn
from typing import Tuple

class OmniM3AEDecoder(nn.Module):
    """
    Decodes the joint representations back into text tokens and image patches.
    """
    def __init__(self, 
                 embed_dim: int = 768, 
                 vocab_size: int = 30522, 
                 patch_size: int = 16, 
                 in_channels: int = 3):
        super().__init__()
        
        # Transformer Decoder stack
        decoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, 
            nhead=12, 
            dim_feedforward=3072, 
            batch_first=True
        )
        self.decoder = nn.TransformerEncoder(decoder_layer, num_layers=4)
        
        # Text reconstruction head (outputs logits over vocabulary)
        self.text_head = nn.Linear(embed_dim, vocab_size)
        
        # Image patch reconstruction head (outputs raw pixel values per patch)
        pixels_per_patch = patch_size * patch_size * in_channels
        self.image_head = nn.Linear(embed_dim, pixels_per_patch)

    def forward(self, 
                joint_features: torch.Tensor, 
                text_mask: torch.Tensor, 
                image_mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        joint_features: (Batch, TotalSeqLen, EmbedDim)
        Returns: Text Logits, Image Reconstructions
        """
        # Pass through decoder blocks
        decoded = self.decoder(joint_features)
        
        # Split representations based on masks/sequence lengths
        # In M3AE, text and image tokens are concatenated: [Text Tokens, Image Tokens]
        B, TotalSeq, D = decoded.shape
        num_text = text_mask.shape[1]
        
        text_features = decoded[:, :num_text, :]
        image_features = decoded[:, num_text:, :]
        
        # Project to target spaces
        text_logits = self.text_head(text_features)
        image_reconstruction = self.image_head(image_features)
        
        return text_logits, image_reconstruction

    def compute_loss(self, 
                     text_logits: torch.Tensor, text_targets: torch.Tensor, text_mask: torch.Tensor,
                     img_recon: torch.Tensor, img_targets: torch.Tensor, img_mask: torch.Tensor) -> torch.Tensor:
        """
        Calculates joint loss: Cross-Entropy for text + MSE for images.
        Masks indicate which tokens/patches were originally masked and need reconstruction loss.
        """
        # Text Loss (only on masked tokens)
        ce_loss = nn.CrossEntropyLoss(reduction='none')
        B, N_t, C = text_logits.shape
        loss_text = ce_loss(text_logits.view(-1, C), text_targets.view(-1)).view(B, N_t)
        loss_text = (loss_text * text_mask).sum() / (text_mask.sum() + 1e-6)
        
        # Image Loss (MSE only on masked patches)
        mse_loss = nn.MSELoss(reduction='none')
        loss_img = mse_loss(img_recon, img_targets).mean(dim=-1) # average over pixels
        loss_img = (loss_img * img_mask).sum() / (img_mask.sum() + 1e-6)
        
        # Total
        return loss_text + loss_img
