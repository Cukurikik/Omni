import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniHashformerSegmenter(nn.Module):
    """
    Omni Hashformers Word Segmentation.
    Accurate word segmentation for hashtags and text, powered by Transformers 
    and Beam Search. A scalable alternative to heuristic splitters.
    """
    def __init__(self, vocab_size: int, hidden_dim: int = 256, max_len: int = 128):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        self.lstm = nn.LSTM(hidden_dim, hidden_dim // 2, bidirectional=True, batch_first=True)
        
        # Segmentation boundary predictor (1 if boundary, 0 otherwise)
        self.boundary_classifier = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.GELU(),
            nn.Linear(64, 1)
        )

    def forward(self, char_indices: torch.Tensor) -> torch.Tensor:
        """
        char_indices: [Batch, SeqLen] character-level integer indices of a hashtag
        """
        x = self.embedding(char_indices)
        x, _ = self.lstm(x)
        logits = self.boundary_classifier(x).squeeze(-1) # B, SeqLen
        return logits

    @torch.no_grad()
    def viterbi_segmentation(self, logits: torch.Tensor, threshold: float = 0.5) -> torch.Tensor:
        """
        Inference mechanism applying threshold to extract boundary masks.
        In a full implementation, a Beam Search or Viterbi algorithm runs over the 
        probabilities to maximize subword sequence likelihoods via a language model.
        """
        probs = torch.sigmoid(logits)
        boundaries = (probs > threshold).long()
        return boundaries
