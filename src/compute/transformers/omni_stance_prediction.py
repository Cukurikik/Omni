"""
omni_stance_prediction.py — Tweet Stance Prediction
Inspired by: tweet-stance-prediction
Layer: Compute / AI

NLP pipeline using deep MLP over frozen transformer embeddings to classify 
the stance of texts towards a specific target (Favor, Against, Neutral).
Zero mock implementation.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniStanceClassifier(nn.Module):
    """
    Takes encoded representations of both the Target Topic and the Tweet Text,
    and predicts the stance relationship via cross-attention and MLP.
    """
    
    def __init__(self, embed_dim: int = 768, hidden_dim: int = 256, num_classes: int = 3):
        super().__init__()
        
        # Cross-Attention mechanism to find correlation between topic and text
        self.cross_attn = nn.MultiheadAttention(embed_dim, num_heads=8, batch_first=True)
        
        self.fc1 = nn.Linear(embed_dim * 2, hidden_dim)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.classifier = nn.Linear(hidden_dim // 2, num_classes)
        
    def forward(self, topic_embeddings: torch.Tensor, text_embeddings: torch.Tensor) -> torch.Tensor:
        """
        topic_embeddings: (Batch, SeqLen1, EmbedDim)
        text_embeddings: (Batch, SeqLen2, EmbedDim)
        """
        # Cross attention: Queries from Text, Keys/Values from Topic
        attn_out, _ = self.cross_attn(query=text_embeddings, key=topic_embeddings, value=topic_embeddings)
        
        # Global average pooling over sequences
        text_pooled = torch.mean(attn_out, dim=1)
        topic_pooled = torch.mean(topic_embeddings, dim=1)
        
        # Combine
        combined = torch.cat([text_pooled, topic_pooled], dim=-1)
        
        # FFN
        x = F.gelu(self.fc1(combined))
        x = self.dropout(x)
        x = F.gelu(self.fc2(x))
        
        logits = self.classifier(x)
        return logits

class OmniStanceLoss(nn.Module):
    """
    Loss function balancing class weights due to heavily skewed dataset distributions
    in real-world stance classification.
    """
    def __init__(self, class_weights: torch.Tensor):
        super().__init__()
        self.loss_fn = nn.CrossEntropyLoss(weight=class_weights, reduction='mean')
        
    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        return self.loss_fn(logits, targets)
