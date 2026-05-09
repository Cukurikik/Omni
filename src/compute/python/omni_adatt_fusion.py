import torch
import torch.nn as nn

# OMNI MOTHER: AdaTT Adaptive Task-to-Task Fusion Network
# Multitask Learning in Recommendations

class OmniAdaTTFusion(nn.Module):
    def __init__(self, num_tasks: int, hidden_dim: int):
        super().__init__()
        self.num_tasks = num_tasks
        
        # Cross-task attention / fusion matrix
        self.task_fusion_weights = nn.Parameter(torch.ones(num_tasks, num_tasks) / num_tasks)
        self.task_transforms = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim) for _ in range(num_tasks)
        ])

    def forward(self, task_embeddings: torch.Tensor) -> torch.Tensor:
        # task_embeddings: [batch, num_tasks, hidden_dim]
        fused_outputs = []
        
        # Softmax over task weights
        fusion_probs = torch.softmax(self.task_fusion_weights, dim=-1)
        
        for t in range(self.num_tasks):
            t_input = task_embeddings[:, t, :]
            t_out = self.task_transforms[t](t_input)
            
            # Fuse with other tasks
            t_fused = torch.zeros_like(t_out)
            for other_t in range(self.num_tasks):
                t_fused += fusion_probs[t, other_t] * task_embeddings[:, other_t, :]
                
            fused_outputs.append(t_fused.unsqueeze(1))
            
        return torch.cat(fused_outputs, dim=1)
