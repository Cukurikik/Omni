"""
OMNI Transformer — Speech/Audio Transformer
Transformer for ASR and audio classification.
Learned from: Whisper architecture patterns
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class AudioTransformerConfig:
    n_mels: int = 80
    embed_dim: int = 512
    num_layers: int = 6
    num_heads: int = 8
    ffn_dim: int = 2048
    max_audio_len: int = 3000  # In mel frames
    vocab_size: int = 51865  # Whisper tokenizer
    dropout: float = 0.1


class AudioEncoder(nn.Module):
    """CNN + Transformer encoder for audio features."""
    def __init__(self, config: AudioTransformerConfig):
        super().__init__()
        self.conv1 = nn.Conv1d(config.n_mels, config.embed_dim, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(config.embed_dim, config.embed_dim, kernel_size=3, stride=2, padding=1)
        self.pos_embed = nn.Embedding(config.max_audio_len, config.embed_dim)
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=config.embed_dim, nhead=config.num_heads,
                dim_feedforward=config.ffn_dim, dropout=config.dropout, batch_first=True,
            ) for _ in range(config.num_layers)
        ])
        self.norm = nn.LayerNorm(config.embed_dim)

    def forward(self, mel_spectrogram: torch.Tensor) -> torch.Tensor:
        # mel: (B, n_mels, T)
        x = F.gelu(self.conv1(mel_spectrogram))
        x = F.gelu(self.conv2(x))
        x = x.transpose(1, 2)  # (B, T', D)
        B, T, D = x.shape
        pos = self.pos_embed(torch.arange(T, device=x.device)).unsqueeze(0)
        x = x + pos
        for layer in self.layers:
            x = layer(x)
        return self.norm(x)


class OmniAudioTransformer(nn.Module):
    """Production audio transformer for ASR."""
    def __init__(self, config: AudioTransformerConfig):
        super().__init__()
        self.encoder = AudioEncoder(config)
        self.decoder_embed = nn.Embedding(config.vocab_size, config.embed_dim)
        self.decoder_pos = nn.Embedding(config.max_audio_len, config.embed_dim)
        self.decoder_layers = nn.ModuleList([
            nn.TransformerDecoderLayer(
                d_model=config.embed_dim, nhead=config.num_heads,
                dim_feedforward=config.ffn_dim, dropout=config.dropout, batch_first=True,
            ) for _ in range(config.num_layers)
        ])
        self.norm = nn.LayerNorm(config.embed_dim)
        self.lm_head = nn.Linear(config.embed_dim, config.vocab_size, bias=False)
        self.config = config

    def forward(self, mel: torch.Tensor, decoder_input_ids: torch.Tensor,
                labels: Optional[torch.Tensor] = None) -> Dict:
        encoder_out = self.encoder(mel)
        B, S = decoder_input_ids.shape
        dec_emb = self.decoder_embed(decoder_input_ids) + self.decoder_pos(torch.arange(S, device=mel.device))
        causal_mask = nn.Transformer.generate_square_subsequent_mask(S, device=mel.device)
        hidden = dec_emb
        for layer in self.decoder_layers:
            hidden = layer(hidden, encoder_out, tgt_mask=causal_mask, tgt_is_causal=True)
        hidden = self.norm(hidden)
        logits = self.lm_head(hidden)
        loss = None
        if labels is not None:
            loss = F.cross_entropy(logits.view(-1, self.config.vocab_size), labels.view(-1), ignore_index=-100)
        return {"logits": logits, "loss": loss, "encoder_output": encoder_out}
