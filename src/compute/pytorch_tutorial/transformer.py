import torch
import torch.nn as nn

class OmniTransformer(nn.Module):
    def __init__(self, d_model=512, nhead=8, num_layers=6):
        super(OmniTransformer, self).__init__()
        self.embedding = nn.Linear(100, d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc_out = nn.Linear(d_model, 10)

    def forward(self, src):
        src = self.embedding(src)
        out = self.transformer_encoder(src)
        return self.fc_out(out)

def initialize_model():
    model = OmniTransformer()
    return model
