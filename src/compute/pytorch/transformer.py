import torch
import torch.nn as nn

class OmniTransformer(nn.Module):
    def __init__(self, d_model=512, nhead=8):
        super().__init__()
        self.encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead)
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layer, num_layers=6)
        self.linear = nn.Linear(d_model, 10)

    def forward(self, src):
        output = self.transformer_encoder(src)
        return self.linear(output)

if __name__ == "__main__":
    model = OmniTransformer()
    src = torch.rand((10, 32, 512))
    out = model(src)
    print(f"Transformer output shape: {out.shape}")
