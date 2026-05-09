"""
OMNI Transformer — NLU Pipeline (Text Classification, NER, Sentiment)
Production NLP pipeline wrapping transformer models.
Learned from: mts-ai/OpenAutoNLU, dipanjanS/adv_nlp_workshop
"""
import torch
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NLUConfig:
    task: str = "classification"
    labels: Optional[List[str]] = None
    max_length: int = 512
    batch_size: int = 32
    device: str = "cuda"
    threshold: float = 0.5


class NLUPipeline:
    """Production NLU pipeline for classification, NER, and sentiment."""
    def __init__(self, model, tokenizer, config: NLUConfig):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.device = torch.device(config.device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device).eval()

    @torch.inference_mode()
    def predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        results = []
        for i in range(0, len(texts), self.config.batch_size):
            batch_texts = texts[i:i + self.config.batch_size]
            encoded = [self.tokenizer.encode(t, max_length=self.config.max_length, padding=True) for t in batch_texts]

            max_len = max(len(e["input_ids"]) for e in encoded)
            input_ids = torch.zeros(len(encoded), max_len, dtype=torch.long)
            attention_mask = torch.zeros(len(encoded), max_len, dtype=torch.long)
            for j, e in enumerate(encoded):
                ids = e["input_ids"]
                input_ids[j, :len(ids)] = torch.tensor(ids)
                attention_mask[j, :len(ids)] = 1

            input_ids = input_ids.to(self.device)
            attention_mask = attention_mask.to(self.device)
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs["logits"]

            if self.config.task == "classification":
                probs = torch.softmax(logits, dim=-1)
                preds = probs.argmax(dim=-1)
                for j in range(len(batch_texts)):
                    label_idx = preds[j].item()
                    label = self.config.labels[label_idx] if self.config.labels else str(label_idx)
                    results.append({"text": batch_texts[j], "label": label, "confidence": probs[j, label_idx].item()})
            elif self.config.task == "ner":
                preds = logits.argmax(dim=-1)
                for j in range(len(batch_texts)):
                    tokens = list(batch_texts[j])[:max_len]
                    entities = []
                    for k, token in enumerate(tokens):
                        if k < preds.size(1):
                            tag_idx = preds[j, k].item()
                            tag = self.config.labels[tag_idx] if self.config.labels else str(tag_idx)
                            if tag != "O":
                                entities.append({"token": token, "tag": tag, "position": k})
                    results.append({"text": batch_texts[j], "entities": entities})
        return results

    @torch.inference_mode()
    def embed(self, texts: List[str]) -> torch.Tensor:
        """Get embeddings for texts."""
        all_embeddings = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            encoded = [self.tokenizer.encode(t, max_length=self.config.max_length) for t in batch]
            max_len = max(len(e["input_ids"]) for e in encoded)
            input_ids = torch.zeros(len(encoded), max_len, dtype=torch.long, device=self.device)
            for j, e in enumerate(encoded):
                ids = e["input_ids"]
                input_ids[j, :len(ids)] = torch.tensor(ids)
            outputs = self.model(input_ids=input_ids)
            hidden = outputs.get("last_hidden_state", outputs.get("logits"))
            all_embeddings.append(hidden.mean(dim=1).cpu())
        return torch.cat(all_embeddings, dim=0)
