# LLM-Workshop — GPT Training Loop Builder
import torch
from typing import Optional, Generic, TypeVar
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class GPTTrainingConfig:
    MAX_BATCH = 1024; MAX_SEQ = 4096; MAX_VOCAB = 200000
    def __init__(self, vocab_size: int, seq_len: int, batch_size: int, lr: float):
        if vocab_size > self.MAX_VOCAB: raise ValueError(f"Vocab exceeds {self.MAX_VOCAB}")
        if seq_len > self.MAX_SEQ: raise ValueError(f"Seq exceeds {self.MAX_SEQ}")
        if batch_size > self.MAX_BATCH: raise ValueError(f"Batch exceeds {self.MAX_BATCH}")
        if lr <= 0 or lr > 1: raise ValueError("LR must be in (0,1]")
        self.vocab_size = vocab_size; self.seq_len = seq_len
        self.batch_size = batch_size; self.lr = lr

    def compute_loss(self, logits: torch.Tensor, targets: torch.Tensor) -> OmniResult[float, str]:
        if logits.dim() != 3: return OmniResult(error="Expected [B,S,V] logits")
        if targets.dim() != 2: return OmniResult(error="Expected [B,S] targets")
        loss = torch.nn.functional.cross_entropy(
            logits.view(-1, logits.size(-1)), targets.view(-1), reduction='mean')
        return OmniResult(value=loss.item())
