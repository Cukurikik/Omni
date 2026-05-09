"""
omni_cnn_text_classifier.py — Fast 1D CNN for Text Classification
Layer: Compute / AI
Inspired by: aniass/Product-Categorization-NLP

Implements Yoon Kim's Convolutional Neural Networks for Sentence Classification.
Provides extremely fast inference for Product Categorization compared to Transformers.
Zero-mock.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class OmniCNNTextClassifier(nn.Module):
    def __init__(
        self, 
        vocab_size: int, 
        embed_dim: int, 
        num_classes: int, 
        kernel_sizes: list = [3, 4, 5], 
        num_filters: int = 100,
        dropout_prob: float = 0.5
    ):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        # Create multiple 1D convolutional layers with different kernel sizes
        # ModuleList ensures they are properly registered
        self.convs = nn.ModuleList([
            nn.Conv1d(
                in_channels=embed_dim, 
                out_channels=num_filters, 
                kernel_size=k
            ) for k in kernel_sizes
        ])
        
        self.dropout = nn.Dropout(dropout_prob)
        self.fc = nn.Linear(len(kernel_sizes) * num_filters, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (Batch, SeqLen) containing token IDs.
        Returns: (Batch, NumClasses) logits.
        """
        # embeds: (Batch, SeqLen, EmbedDim)
        embeds = self.embedding(x)
        
        # Conv1D expects (Batch, Channels, Length), so we transpose
        # embeds: (Batch, EmbedDim, SeqLen)
        embeds = embeds.transpose(1, 2)
        
        # Apply convolution and ReLU to each filter size
        # resulting shape for each: (Batch, NumFilters, SeqLen - KernelSize + 1)
        conv_results = [F.relu(conv(embeds)) for conv in self.convs]
        
        # Global Max Pooling 1D
        # resulting shape for each: (Batch, NumFilters, 1) -> squeezed to (Batch, NumFilters)
        pooled_results = [F.max_pool1d(res, res.shape[2]).squeeze(2) for res in conv_results]
        
        # Concatenate all pooled features
        # cat_out: (Batch, NumFilters * len(kernel_sizes))
        cat_out = torch.cat(pooled_results, dim=1)
        
        # Apply dropout
        drop_out = self.dropout(cat_out)
        
        # Final classification layer
        logits = self.fc(drop_out)
        
        return logits
