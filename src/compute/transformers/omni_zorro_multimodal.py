"""
omni_zorro_multimodal.py — Zorro Masked Multimodal Transformer
Layer: Compute / AI
Inspired by: lucidrains/zorro-pytorch

Implements the Zorro Transformer architecture which allows separate modalities
(audio, video, text) to interact selectively using specialized attention masks,
preventing early cross-contamination of independent features. Zero mock.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniZorroMask(nn.Module):
    @staticmethod
    def generate_mask(seq_len_audio: int, seq_len_video: int, seq_len_text: int, device: torch.device) -> torch.Tensor:
        """
        Generates the Zorro masking matrix.
        Audio only attends to Audio.
        Video only attends to Video.
        Text attends to Text, Audio, and Video (Fusion occurs in Text).
        """
        total_len = seq_len_audio + seq_len_video + seq_len_text
        mask = torch.ones((total_len, total_len), dtype=torch.bool, device=device)
        
        idx_a_end = seq_len_audio
        idx_v_end = seq_len_audio + seq_len_video
        
        # Audio attending to Audio: Unmask (False means do not mask)
        mask[:idx_a_end, :idx_a_end] = False
        
        # Video attending to Video: Unmask
        mask[idx_a_end:idx_v_end, idx_a_end:idx_v_end] = False
        
        # Text attending to everything (Text, Audio, Video): Unmask
        mask[idx_v_end:, :] = False
        
        return mask

class OmniZorroBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, mlp_ratio: float = 4.0):
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.attn = nn.MultiheadAttention(embed_dim=d_model, num_heads=n_heads, batch_first=True)
        self.norm2 = nn.LayerNorm(d_model)
        self.mlp = nn.Sequential(
            nn.Linear(d_model, int(d_model * mlp_ratio)),
            nn.GELU(),
            nn.Linear(int(d_model * mlp_ratio), d_model)
        )

    def forward(self, x: torch.Tensor, attn_mask: torch.Tensor) -> torch.Tensor:
        # Attention phase
        x_norm = self.norm1(x)
        # PyTorch MHA mask: True means DO NOT attend
        attn_out, _ = self.attn(query=x_norm, key=x_norm, value=x_norm, attn_mask=attn_mask, need_weights=False)
        x = x + attn_out
        
        # MLP phase
        x = x + self.mlp(self.norm2(x))
        return x

class OmniZorroTransformer(nn.Module):
    def __init__(self, d_model: int, n_heads: int, depth: int):
        super().__init__()
        self.layers = nn.ModuleList([OmniZorroBlock(d_model, n_heads) for _ in range(depth)])
        self.final_norm = nn.LayerNorm(d_model)

    def forward(self, audio_tokens: torch.Tensor, video_tokens: torch.Tensor, text_tokens: torch.Tensor):
        """
        Inputs shape: (Batch, SeqLen, D)
        """
        B, L_a, D = audio_tokens.shape
        _, L_v, _ = video_tokens.shape
        _, L_t, _ = text_tokens.shape

        # Concatenate modalities
        x = torch.cat([audio_tokens, video_tokens, text_tokens], dim=1) # (B, L_a + L_v + L_t, D)
        
        # Generate Zorro Modal Isolation Mask
        # Shape: (TotalLen, TotalLen)
        zorro_mask = OmniZorroMask.generate_mask(L_a, L_v, L_t, device=x.device)

        # Pass through layers
        for layer in self.layers:
            x = layer(x, attn_mask=zorro_mask)

        x = self.final_norm(x)
        
        # Return fused text tokens (which contain cross-modal context)
        return x[:, (L_a + L_v):, :]
