import torch
import torch.nn as nn
from typing import List, Dict, Any, Tuple

class OmniResult:
    def __init__(self, ok: Any = None, err: str = None):
        self.ok = ok
        self.err = err
    
    def is_ok(self) -> bool:
        return self.err is None
        
    def unwrap(self) -> Any:
        if not self.is_ok():
            raise RuntimeError(f"Unwrap failed: {self.err}")
        return self.ok

# Structural mock of BERT model for zero-mock interface bridging
class MinimalBERTForTokenClassification(nn.Module):
    def __init__(self, vocab_size: int = 30522, hidden_size: int = 768, num_labels: int = 9):
        super().__init__()
        self.embeddings = nn.Embedding(vocab_size, hidden_size)
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=hidden_size, nhead=8, batch_first=True),
            num_layers=2 # Shallow for representation
        )
        self.classifier = nn.Linear(hidden_size, num_labels)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        x = self.embeddings(input_ids)
        x = self.encoder(x, src_key_padding_mask=~attention_mask.bool())
        return self.classifier(x)

class BERTNEREngine:
    def __init__(self, num_labels: int = 9, device: str = 'cpu'):
        self.device = torch.device(device)
        self.model = MinimalBERTForTokenClassification(num_labels=num_labels).to(self.device)
        self.model.eval()
        
        # Standard CoNLL-2003 NER tags
        self.id2label = {
            0: "O", 1: "B-PER", 2: "I-PER", 3: "B-ORG", 4: "I-ORG", 
            5: "B-LOC", 6: "I-LOC", 7: "B-MISC", 8: "I-MISC"
        }

    def predict_entities(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> OmniResult:
        try:
            input_ids = input_ids.to(self.device)
            attention_mask = attention_mask.to(self.device)

            with torch.no_grad():
                logits = self.model(input_ids, attention_mask)
            
            # shape: (batch_size, seq_len, num_labels)
            predictions = torch.argmax(logits, dim=2)
            
            # Map back to labels
            batch_entities = []
            for batch_idx in range(predictions.size(0)):
                entities = []
                for seq_idx in range(predictions.size(1)):
                    # Ignore padding (mask == 0)
                    if attention_mask[batch_idx, seq_idx] == 1:
                        pred_id = predictions[batch_idx, seq_idx].item()
                        entities.append(self.id2label[pred_id])
                batch_entities.append(entities)

            return OmniResult(ok=batch_entities)
            
        except Exception as e:
            return OmniResult(err=f"NER prediction failed: {str(e)}")
