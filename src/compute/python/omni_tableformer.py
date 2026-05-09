import torch
import torch.nn as nn

class OmniTableFormer(nn.Module):
    """OMNI Implementation of Table-Text Encoding (inspired by TableFormer)"""
    def __init__(self, hidden_dim=768, num_heads=12):
        super().__init__()
        self.encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim, 
            nhead=num_heads, 
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(self.encoder_layer, num_layers=6)
        self.row_embeddings = nn.Embedding(512, hidden_dim)
        self.col_embeddings = nn.Embedding(512, hidden_dim)

    def forward(self, text_embeds, row_ids, col_ids):
        # Inject tabular structural embeddings into text features
        tabular_bias = self.row_embeddings(row_ids) + self.col_embeddings(col_ids)
        x = text_embeds + tabular_bias
        return self.transformer(x)
