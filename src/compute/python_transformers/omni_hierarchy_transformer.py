import torch
import torch.nn as nn
from transformers import AutoModel

class OmniHierarchyTransformer(nn.Module):
    """
    Implements Language Models as Hierarchy Encoders (HiT).
    Maps text into a hyperbolic space or hierarchical structured space
    to capture ontological relationships like IS-A or PART-OF directly in the embedding space.
    """
    def __init__(self, base_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model_name)
        self.hidden_size = self.encoder.config.hidden_size
        
        # Projection head to a hyperbolic-friendly space
        self.hierarchy_projection = nn.Sequential(
            nn.Linear(self.hidden_size, self.hidden_size),
            nn.ReLU(),
            nn.Linear(self.hidden_size, self.hidden_size)
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        # Mean pooling
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
        embeddings = torch.sum(outputs.last_hidden_state * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        
        # Map to hierarchical space
        hierarchy_emb = self.hierarchy_projection(embeddings)
        
        # Normalize to Poincare ball (simplistic projection)
        norm = torch.norm(hierarchy_emb, p=2, dim=-1, keepdim=True)
        hierarchy_emb = hierarchy_emb / (norm + 1e-5) * 0.99
        
        return hierarchy_emb

    def compute_poincare_distance(self, u, v):
        """Computes distance in Poincare Ball."""
        sq_u = torch.sum(u ** 2, dim=-1)
        sq_v = torch.sum(v ** 2, dim=-1)
        sq_dist = torch.sum((u - v) ** 2, dim=-1)
        
        denominator = (1 - sq_u) * (1 - sq_v)
        denominator = torch.clamp(denominator, min=1e-5)
        
        x = 1 + 2 * sq_dist / denominator
        # arcosh(x) = ln(x + sqrt(x^2 - 1))
        dist = torch.log(x + torch.sqrt(x**2 - 1))
        return dist
