import torch
import torch.nn as nn

class TabPFNTransformer(nn.Module):
    """
    OMNI Engine: TabPFN Core Transformer architecture for tabular data.
    """
    def __init__(self, embed_dim=512, num_heads=8, num_layers=12):
        super().__init__()
        self.encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, 
            nhead=num_heads, 
            dim_feedforward=embed_dim * 4,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(self.encoder_layer, num_layers=num_layers)
        
        # Feature embeddings for tabular columns
        self.feature_embed = nn.Linear(1, embed_dim)

    def forward(self, x):
        # x shape: (batch_size, num_features)
        # Transform tabular data into sequence of embeddings
        x_seq = x.unsqueeze(-1) # (batch_size, num_features, 1)
        embeddings = self.feature_embed(x_seq) # (batch_size, num_features, embed_dim)
        
        out = self.transformer(embeddings)
        # Pooling over sequence length
        return out.mean(dim=1)
