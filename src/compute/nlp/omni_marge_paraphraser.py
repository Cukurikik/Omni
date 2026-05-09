import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniMargeParaphraser(nn.Module):
    """
    Omni MARGE Paraphraser.
    Pre-training via Paraphrasing (MARGE) implementation.
    The model learns by reconstructing target documents given a set of retrieved 
    evidence documents in multiple languages or paraphrased forms.
    """
    def __init__(self, vocab_size: int, hidden_dim: int = 768, num_layers: int = 6):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        
        # We need a cross-attention encoder-decoder architecture
        encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=8, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        decoder_layer = nn.TransformerDecoderLayer(d_model=hidden_dim, nhead=8, batch_first=True)
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)
        
        self.lm_head = nn.Linear(hidden_dim, vocab_size)

    def forward(self, evidence_docs: torch.Tensor, target_doc: torch.Tensor) -> torch.Tensor:
        """
        evidence_docs: [Batch, Num_Docs, SeqLen]
        target_doc: [Batch, SeqLen]
        """
        B, N_docs, E_len = evidence_docs.shape
        _, T_len = target_doc.shape
        
        # Flatten evidence docs into a single long sequence per batch for the encoder
        # B, (N_docs * E_len)
        flat_evidence = evidence_docs.view(B, -1)
        
        # Encode evidence
        evidence_emb = self.embedding(flat_evidence)
        memory = self.encoder(evidence_emb) # B, (N_docs * E_len), H
        
        # Decode target
        target_emb = self.embedding(target_doc)
        
        # Causal mask for autoregressive decoding
        tgt_mask = nn.Transformer.generate_square_subsequent_mask(T_len, device=target_doc.device)
        
        output = self.decoder(target_emb, memory, tgt_mask=tgt_mask)
        logits = self.lm_head(output)
        
        return logits
