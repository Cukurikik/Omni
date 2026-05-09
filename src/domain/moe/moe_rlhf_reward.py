"""
moe_rlhf_reward.py — Domain / Alignment
Layer: Domain / AI — MoE RLHF Reward Model

Integrates Mixture-of-Experts directly into the RLHF (Reinforcement Learning from 
Human Feedback) reward model. Different experts learn to score different human
preferences (e.g., Expert 0: Toxicity, Expert 1: Helpfulness, Expert 2: Humor),
and the router combines them into a single scalar reward.
"""
import torch
import torch.nn as nn

class AlignmentExpert(nn.Module):
    """An expert that scores a specific alignment axis."""
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.scorer = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1) # Outputs scalar reward
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.scorer(x)

class MoERewardModel(nn.Module):
    """
    Reward Model utilizing MoE to score generated sequences.
    Takes final hidden states from the LLM and produces a reward score.
    """
    def __init__(self, hidden_dim: int, num_experts: int = 4):
        super().__init__()
        
        # Router decides which preference axis is most relevant to the prompt
        self.router = nn.Linear(hidden_dim, num_experts)
        
        # Experts evaluate specific alignment axes
        self.experts = nn.ModuleList([
            AlignmentExpert(hidden_dim) for _ in range(num_experts)
        ])

    def forward(self, final_hidden_state: torch.Tensor) -> torch.Tensor:
        """
        final_hidden_state: (Batch, hidden_dim) representing the EOS token embedding
        Returns: (Batch, 1) Scalar reward
        """
        # 1. Routing
        # What kind of query is this? (Math, Chat, Coding) -> Router learns this
        router_logits = self.router(final_hidden_state)
        routing_weights = torch.softmax(router_logits, dim=-1) # (B, num_experts)
        
        # 2. Get rewards from all experts
        expert_rewards = []
        for expert in self.experts:
            expert_rewards.append(expert(final_hidden_state)) # (B, 1)
            
        stacked_rewards = torch.cat(expert_rewards, dim=1) # (B, num_experts)
        
        # 3. Final blended reward
        final_reward = torch.sum(stacked_rewards * routing_weights, dim=1, keepdim=True)
        
        return final_reward
