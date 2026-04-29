# KnowLM Knowledge-Grounded Training Pipeline
# Production LoRA + Knowledge Injection trainer

import torch
from typing import Optional, Generic, TypeVar

T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class KnowLMTrainer:
    MAX_SEQ_LEN = 32768
    MAX_BATCH = 64

    def __init__(self, model, lr: float = 2e-5):
        self.model = model
        self.lr = lr
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    def train_step(self, input_ids: torch.Tensor, labels: torch.Tensor, kg_embeddings: Optional[torch.Tensor] = None) -> OmniResult[float, str]:
        if input_ids.shape[1] > self.MAX_SEQ_LEN:
            return OmniResult(error=f"Seq len {input_ids.shape[1]} exceeds {self.MAX_SEQ_LEN}")
        if input_ids.shape[0] > self.MAX_BATCH:
            return OmniResult(error=f"Batch size {input_ids.shape[0]} exceeds {self.MAX_BATCH}")
        try:
            self.optimizer.zero_grad()
            outputs = self.model(input_ids=input_ids, labels=labels)
            loss = outputs.loss
            if kg_embeddings is not None:
                kg_loss = self._knowledge_alignment_loss(outputs.hidden_states, kg_embeddings)
                loss = loss + 0.1 * kg_loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            return OmniResult(value=loss.item())
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                torch.cuda.empty_cache()
                return OmniResult(error="CUDA OOM during training")
            return OmniResult(error=str(e))

    def _knowledge_alignment_loss(self, hidden_states, kg_emb: torch.Tensor) -> torch.Tensor:
        last_hidden = hidden_states[-1] if isinstance(hidden_states, tuple) else hidden_states
        pooled = last_hidden.mean(dim=1)
        return torch.nn.functional.mse_loss(pooled, kg_emb[:pooled.shape[0]])
