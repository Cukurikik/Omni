"""
omni_ner_span.py — Span-based Named Entity Recognition
Inspired by: nerpy (Implementation of NER using Python/BertSpan)
Layer: Compute / AI

Predicts entity spans directly by predicting the start and end tokens of an entity,
handling nested entities better than standard sequence labeling (BIO).
"""

import torch
import torch.nn as nn
from typing import Dict, Optional, Tuple

class OmniSpanNER(nn.Module):
    """Span-based NER model using a Transformer encoder backbone."""

    def __init__(self, hidden_size: int = 768, num_labels: int = 10, dropout: float = 0.1):
        super().__init__()
        self.num_labels = num_labels
        
        # In a real scenario, this is a pre-trained BERT/RoBERTa encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size, 
            nhead=12, 
            dim_feedforward=3072, 
            dropout=dropout,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=6)
        self.dropout = nn.Dropout(dropout)
        
        # Heads for predicting start and end of spans
        self.start_head = nn.Linear(hidden_size, num_labels)
        self.end_head = nn.Linear(hidden_size, num_labels)

    def forward(self, 
                input_embeddings: torch.Tensor, 
                attention_mask: torch.Tensor,
                start_positions: Optional[torch.Tensor] = None,
                end_positions: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """
        Args:
            input_embeddings: (B, S, D)
            attention_mask: (B, S)
            start_positions: (B, S, L) optional one-hot or soft labels
            end_positions: (B, S, L) optional one-hot or soft labels
        """
        # (B, S, D)
        padding_mask = ~attention_mask.bool()
        sequence_output = self.encoder(input_embeddings, src_key_padding_mask=padding_mask)
        sequence_output = self.dropout(sequence_output)
        
        # (B, S, L)
        start_logits = self.start_head(sequence_output)
        end_logits = self.end_head(sequence_output)
        
        loss = None
        if start_positions is not None and end_positions is not None:
            loss_fct = nn.BCEWithLogitsLoss(reduction='none')
            
            # Active mask prevents calculating loss on padded tokens
            active_loss = attention_mask.unsqueeze(-1).expand_as(start_logits).bool()
            
            start_loss = loss_fct(start_logits, start_positions.float())
            start_loss = start_loss.masked_select(active_loss).mean()
            
            end_loss = loss_fct(end_logits, end_positions.float())
            end_loss = end_loss.masked_select(active_loss).mean()
            
            loss = start_loss + end_loss

        return {
            "loss": loss,
            "start_logits": start_logits,
            "end_logits": end_logits
        }

    def decode(self, start_logits: torch.Tensor, end_logits: torch.Tensor, threshold: float = 0.5) -> list:
        """Decodes raw logits into entity spans."""
        start_probs = torch.sigmoid(start_logits)
        end_probs = torch.sigmoid(end_logits)
        
        B, S, L = start_probs.shape
        predictions = []
        
        for b in range(B):
            batch_preds = []
            for l in range(1, L): # skip 0 if it's the 'O' background class
                starts = torch.where(start_probs[b, :, l] > threshold)[0]
                ends = torch.where(end_probs[b, :, l] > threshold)[0]
                
                # Match starts and ends greedily
                for start in starts:
                    valid_ends = ends[ends >= start]
                    if len(valid_ends) > 0:
                        end = valid_ends[0]
                        # Score is average of start and end probability
                        score = (start_probs[b, start, l] + end_probs[b, end, l]) / 2.0
                        batch_preds.append({
                            "start": start.item(),
                            "end": end.item(),
                            "label_id": l,
                            "score": score.item()
                        })
            predictions.append(batch_preds)
            
        return predictions
