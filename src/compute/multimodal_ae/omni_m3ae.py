"""
omni_m3ae.py — Multimodal Masked Autoencoder
Inspired by: M3AE (Multimodal Masked Autoencoders)
Layer: Compute / AI

Implementation of a unified architecture that masks and reconstructs
both image patches and text tokens simultaneously.
"""

import torch
import torch.nn as nn
from typing import Dict

class MultimodalMaskedAutoencoder(nn.Module):
    """M3AE: Multimodal Masked Autoencoder for joint image and text pretraining."""

    def __init__(self, 
                 embed_dim: int = 768, 
                 vocab_size: int = 30000, 
                 img_size: int = 224, 
                 patch_size: int = 16):
        super().__init__()
        self.embed_dim = embed_dim
        
        # --- Modality Encoders ---
        # Text
        self.text_embed = nn.Embedding(vocab_size, embed_dim)
        
        # Image patches
        self.num_patches = (img_size // patch_size) ** 2
        self.patch_embed = nn.Conv2d(3, embed_dim, kernel_size=patch_size, stride=patch_size)
        
        # Type and position embeddings
        self.modality_type_embed = nn.Embedding(2, embed_dim) # 0: text, 1: image
        self.text_pos_embed = nn.Parameter(torch.zeros(1, 512, embed_dim))
        self.img_pos_embed = nn.Parameter(torch.zeros(1, self.num_patches, embed_dim))
        
        # --- Shared Encoder ---
        encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=12, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=12)
        
        # --- Shared Decoder ---
        # Decoder usually has lower depth
        self.mask_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        decoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=12, batch_first=True)
        self.decoder = nn.TransformerEncoder(decoder_layer, num_layers=4)
        
        # --- Heads ---
        self.text_head = nn.Linear(embed_dim, vocab_size)
        self.img_head = nn.Linear(embed_dim, 3 * patch_size ** 2)

    def forward(self, 
                text_ids: torch.Tensor, 
                images: torch.Tensor, 
                text_mask_ratio: float = 0.15,
                img_mask_ratio: float = 0.75) -> Dict[str, torch.Tensor]:
        """
        Forward pass applying high masking ratios to both modalities.
        """
        B, seq_len = text_ids.shape
        
        # 1. Embed inputs
        t_emb = self.text_embed(text_ids) + self.text_pos_embed[:, :seq_len, :] + self.modality_type_embed(torch.tensor(0).to(text_ids.device))
        
        i_emb = self.patch_embed(images).flatten(2).transpose(1, 2) # (B, N, D)
        i_emb = i_emb + self.img_pos_embed + self.modality_type_embed(torch.tensor(1).to(images.device))
        
        # 2. Generate random masks
        t_mask = torch.rand(B, seq_len, device=text_ids.device) < text_mask_ratio
        i_mask = torch.rand(B, self.num_patches, device=images.device) < img_mask_ratio
        
        # 3. Filter inputs (only keep unmasked)
        # For variable length sequences, we use lists or padded tensors. 
        # Here we mask with 0s for the encoder and drop later, or use attention masking.
        # Standard MAE actually drops tokens to speed up.
        # We will keep them but mask them out in attention for simplicity in this implementation.
        t_visible = t_emb.clone()
        t_visible[t_mask] = 0.0 # dropped
        
        i_visible = i_emb.clone()
        i_visible[i_mask] = 0.0 # dropped
        
        # Concat
        x = torch.cat([t_visible, i_visible], dim=1)
        
        # Encoder attention mask (ignore dropped tokens)
        attn_mask = torch.cat([~t_mask, ~i_mask], dim=1) # True means visible
        
        # 4. Shared Encoder
        encoded = self.encoder(x, src_key_padding_mask=~attn_mask)
        
        # 5. Prepare for Decoder
        # Replace dropped slots with mask tokens
        decoder_input = encoded.clone()
        mask_tokens = self.mask_token.expand(B, seq_len + self.num_patches, -1)
        
        # Create full mask boolean
        full_mask = torch.cat([t_mask, i_mask], dim=1)
        decoder_input[full_mask] = mask_tokens[full_mask]
        
        # Add pos embeddings again for decoder
        t_pos_full = self.text_pos_embed[:, :seq_len, :].expand(B, -1, -1)
        i_pos_full = self.img_pos_embed.expand(B, -1, -1)
        full_pos = torch.cat([t_pos_full, i_pos_full], dim=1)
        
        decoder_input = decoder_input + full_pos
        
        # 6. Shared Decoder
        decoded = self.decoder(decoder_input)
        
        # 7. Split and compute loss
        dec_text = decoded[:, :seq_len, :]
        dec_img = decoded[:, seq_len:, :]
        
        text_logits = self.text_head(dec_text)
        img_preds = self.img_head(dec_img)
        
        # Only compute loss on masked tokens
        text_loss = F.cross_entropy(text_logits[t_mask], text_ids[t_mask])
        
        # Get target pixel values (normalized)
        patch_size = int(self.img_head.out_features / 3) ** 0.5
        target_img = self.patchify(images, int(patch_size))
        img_loss = F.mse_loss(img_preds[i_mask], target_img[i_mask])
        
        return {
            "loss": text_loss + img_loss,
            "text_loss": text_loss,
            "img_loss": img_loss
        }

    def patchify(self, imgs: torch.Tensor, p: int) -> torch.Tensor:
        """
        imgs: (N, 3, H, W)
        x: (N, L, patch_size**2 *3)
        """
        assert imgs.shape[2] == imgs.shape[3] and imgs.shape[2] % p == 0
        h = w = imgs.shape[2] // p
        x = imgs.reshape(shape=(imgs.shape[0], 3, h, p, w, p))
        x = torch.einsum('nchpwq->nhwpqc', x)
        x = x.reshape(shape=(imgs.shape[0], h * w, p**2 * 3))
        return x
