import torch
import torch.nn as nn
from transformers import AutoModel

class OmniTransformerEmbedder(nn.Module):
    """
    OMNI Framework - Transformers Embedder
    Zero-mock implementation of a word-level transformer embedding layer.
    Extracts and aggregates hidden states from pretrained transformers to form
    robust word representations.
    """
    def __init__(self, model_name: str = "bert-base-uncased", pooling_strategy: str = "mean", layers: list[int] = [-1, -2, -3, -4]):
        super().__init__()
        self.transformer = AutoModel.from_pretrained(model_name, output_hidden_states=True)
        self.pooling_strategy = pooling_strategy
        self.layers = layers
        self.embedding_dim = self.transformer.config.hidden_size

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        all_hidden_states = outputs.hidden_states # Tuple of layers

        # Stack the selected layers
        selected_states = torch.stack([all_hidden_states[i] for i in self.layers]) # (num_layers, B, S, dim)

        # Aggregate across layers
        if self.pooling_strategy == "mean":
            word_embeddings = torch.mean(selected_states, dim=0)
        elif self.pooling_strategy == "sum":
            word_embeddings = torch.sum(selected_states, dim=0)
        elif self.pooling_strategy == "last":
            word_embeddings = selected_states[-1]
        else:
            raise ValueError(f"Unknown pooling strategy: {self.pooling_strategy}")

        return word_embeddings # (B, S, dim)
