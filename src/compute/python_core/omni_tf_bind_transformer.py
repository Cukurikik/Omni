import torch
import torch.nn as nn
from typing import Optional, Any, Dict

class Result:
    def __init__(self, value: Any = None, error: Optional[Exception] = None):
        self.value = value
        self.error = error
        self.is_success = error is None

    @classmethod
    def ok(cls, value: Any) -> 'Result':
        return cls(value=value)

    @classmethod
    def fail(cls, error: Exception) -> 'Result':
        return cls(error=error)

class TFBindTransformerArch(nn.Module):
    """
    Transformer model for DNA <-> Transcription Factor Binding.
    Based on lucidrains/tf-bind-transformer architecture.
    """
    def __init__(self, vocab_size: int = 5, dim: int = 256, depth: int = 6, heads: int = 8, seq_len: int = 100):
        super().__init__()
        self.seq_len = seq_len
        # DNA Vocabulary: A, C, G, T, N (padding/unknown)
        self.token_emb = nn.Embedding(vocab_size, dim)
        self.pos_emb = nn.Embedding(seq_len, dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=dim, 
            nhead=heads, 
            dim_feedforward=dim * 4, 
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=depth)
        
        # Binary classification for binding (Binding / No Binding)
        self.to_logits = nn.Sequential(
            nn.Linear(dim, dim),
            nn.GELU(),
            nn.Linear(dim, 1)
        )

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        b, n = x.shape
        pos = torch.arange(n, device=x.device)
        
        x = self.token_emb(x) + self.pos_emb(pos)
        x = self.transformer(x, src_key_padding_mask=mask)
        
        # Global Average Pooling
        x = x.mean(dim=1)
        return self.to_logits(x).squeeze(-1)

class OmniTFBindingEngine:
    """
    OMNI Compute Layer: DNA Transcription Factor Binding Prediction Engine.
    Uses transformer models to predict transcription factor binding from DNA sequences.
    """
    def __init__(self, config: Dict[str, Any]):
        self.vocab_size = config.get("vocab_size", 5)
        self.seq_len = config.get("seq_len", 100)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = TFBindTransformerArch(
            vocab_size=self.vocab_size, 
            seq_len=self.seq_len
        ).to(self.device)

    def initialize(self) -> Result:
        try:
            # Init parameters
            for p in self.model.parameters():
                if p.dim() > 1:
                    nn.init.xavier_uniform_(p)
            return Result.ok(True)
        except Exception as e:
            return Result.fail(e)

    def encode_dna(self, sequences: list[str]) -> torch.Tensor:
        """Encodes DNA string 'ACGT' to tensor representation."""
        mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'N': 4}
        encoded = []
        for seq in sequences:
            # Pad or truncate to seq_len
            seq = seq.upper().ljust(self.seq_len, 'N')[:self.seq_len]
            encoded.append([mapping.get(n, 4) for n in seq])
        return torch.tensor(encoded, dtype=torch.long)

    def predict_binding(self, dna_sequences: list[str]) -> Result:
        """
        Predicts whether a transcription factor binds to the provided DNA sequences.
        """
        try:
            tensor_seqs = self.encode_dna(dna_sequences).to(self.device)
            # Create padding mask (True for padding token 'N' which is 4)
            pad_mask = (tensor_seqs == 4)
            
            self.model.eval()
            with torch.no_grad():
                logits = self.model(tensor_seqs, mask=pad_mask)
                probs = torch.sigmoid(logits)
                
            return Result.ok(probs.cpu().tolist())
        except Exception as e:
            return Result.fail(e)

def build_tf_binding_engine() -> Result:
    config = {"vocab_size": 5, "seq_len": 100}
    engine = OmniTFBindingEngine(config)
    return Result.ok(engine)
