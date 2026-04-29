import torch
import torch.nn.functional as F

class PPOUpdater:
    """
    OMNI Engine: rllm Proximal Policy Optimization (PPO) updater for RLHF.
    """
    def __init__(self, policy, value_model, clip_ratio=0.2, c1=1.0, c2=0.01):
        self.policy = policy
        self.value_model = value_model
        self.clip_ratio = clip_ratio
        self.c1 = c1
        self.c2 = c2

    def update(self, states, actions, log_probs_old, returns, advantages):
        # 1. Get new log probs and values
        logits = self.policy(states)
        values = self.value_model(states).squeeze(-1)
        
        # Log prob calculation (simplified for engine representation)
        dist = torch.distributions.Categorical(logits=logits)
        log_probs_new = dist.log_prob(actions)
        entropy = dist.entropy().mean()

        # 2. PPO Policy Loss
        ratio = torch.exp(log_probs_new - log_probs_old)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1.0 - self.clip_ratio, 1.0 + self.clip_ratio) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()

        # 3. Value Loss
        value_loss = F.mse_loss(values, returns)

        # 4. Total Loss
        loss = policy_loss + self.c1 * value_loss - self.c2 * entropy
        return loss
