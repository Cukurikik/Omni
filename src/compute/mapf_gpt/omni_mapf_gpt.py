"""
omni_mapf_gpt.py — Multi-Agent Pathfinding with GPT Architecture
Inspired by: CognitiveAISystems/MAPF-GPT (AAAI 2025)
Layer: Compute / AI

Decentralized MAPF solver using imitation learning from LaCAM expert trajectories.
Transformer predicts agent actions from partial observations without heuristics.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import IntEnum


class AgentAction(IntEnum):
    STAY = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


@dataclass
class MAPFConfig:
    obs_radius: int = 5
    obs_channels: int = 4  # obstacles, other_agents, goal, history
    dim: int = 256
    depth: int = 8
    heads: int = 8
    dim_head: int = 32
    ff_mult: int = 4
    num_actions: int = 5
    max_agents: int = 256
    max_timesteps: int = 128
    dropout: float = 0.1


class ObservationEncoder(nn.Module):
    """Encodes the local observation grid into a feature vector."""

    def __init__(self, config: MAPFConfig):
        super().__init__()
        obs_size = 2 * config.obs_radius + 1
        self.conv_net = nn.Sequential(
            nn.Conv2d(config.obs_channels, 32, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(3),
            nn.Flatten(),
            nn.Linear(64 * 9, config.dim),
            nn.LayerNorm(config.dim),
        )

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        return self.conv_net(obs)


class AgentPositionEncoding(nn.Module):
    """Relative position encoding for agent's goal direction."""

    def __init__(self, dim: int):
        super().__init__()
        self.goal_proj = nn.Sequential(
            nn.Linear(4, dim),
            nn.GELU(),
            nn.Linear(dim, dim),
        )

    def forward(self, dx: torch.Tensor, dy: torch.Tensor) -> torch.Tensor:
        """dx, dy: relative displacement to goal, shape (B,)."""
        dist = torch.sqrt(dx.float() ** 2 + dy.float() ** 2 + 1e-8)
        angle = torch.atan2(dy.float(), dx.float())
        features = torch.stack([dx.float(), dy.float(), dist, angle], dim=-1)
        return self.goal_proj(features)


class MAPFTransformerBlock(nn.Module):
    def __init__(self, dim: int, heads: int, dim_head: int, ff_mult: int,
                 dropout: float):
        super().__init__()
        self.attn_norm = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(dim, heads, dropout=dropout, batch_first=True)
        self.ff_norm = nn.LayerNorm(dim)
        self.ff = nn.Sequential(
            nn.Linear(dim, dim * ff_mult),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(dim * ff_mult, dim),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        normed = self.attn_norm(x)
        causal_mask = torch.triu(
            torch.ones(x.shape[1], x.shape[1], device=x.device, dtype=torch.bool), diagonal=1
        )
        attn_out, _ = self.attn(normed, normed, normed, attn_mask=causal_mask)
        x = x + attn_out
        x = x + self.ff(self.ff_norm(x))
        return x


class OmniMAPFGPT(nn.Module):
    """MAPF-GPT: Transformer-based decentralized pathfinder.

    Trained via imitation learning on 3M+ LaCAM expert trajectories.
    At inference, predicts actions from local observations without
    communication between agents or search-based heuristics.

    Each agent independently runs this model on its local observation
    history to predict the next best action.
    """

    def __init__(self, config: MAPFConfig):
        super().__init__()
        self.config = config

        self.obs_encoder = ObservationEncoder(config)
        self.goal_encoder = AgentPositionEncoding(config.dim)
        self.timestep_embed = nn.Embedding(config.max_timesteps, config.dim)
        self.action_embed = nn.Embedding(config.num_actions, config.dim)

        self.combine_proj = nn.Sequential(
            nn.Linear(config.dim * 3, config.dim),
            nn.GELU(),
            nn.LayerNorm(config.dim),
        )

        self.transformer = nn.ModuleList([
            MAPFTransformerBlock(
                config.dim, config.heads, config.dim_head,
                config.ff_mult, config.dropout
            )
            for _ in range(config.depth)
        ])
        self.final_norm = nn.LayerNorm(config.dim)
        self.action_head = nn.Linear(config.dim, config.num_actions)
        self.value_head = nn.Linear(config.dim, 1)

    def encode_step(
        self,
        obs: torch.Tensor,
        goal_dx: torch.Tensor,
        goal_dy: torch.Tensor,
        timestep: torch.Tensor,
    ) -> torch.Tensor:
        """Encode a single timestep of observation."""
        obs_feat = self.obs_encoder(obs)
        goal_feat = self.goal_encoder(goal_dx, goal_dy)
        time_feat = self.timestep_embed(timestep)
        combined = torch.cat([obs_feat, goal_feat, time_feat], dim=-1)
        return self.combine_proj(combined)

    def forward(
        self,
        observations: torch.Tensor,
        goal_dx: torch.Tensor,
        goal_dy: torch.Tensor,
        timesteps: torch.Tensor,
        actions: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        """
        Args:
            observations: (B, T, C, H, W) observation history
            goal_dx: (B, T) relative x to goal at each step
            goal_dy: (B, T) relative y to goal at each step
            timesteps: (B, T) timestep indices
            actions: (B, T) ground truth actions for training
        """
        b, t = observations.shape[:2]
        device = observations.device

        tokens = []
        for step in range(t):
            tok = self.encode_step(
                observations[:, step],
                goal_dx[:, step],
                goal_dy[:, step],
                timesteps[:, step],
            )
            tokens.append(tok)

        x = torch.stack(tokens, dim=1)

        for block in self.transformer:
            x = block(x)

        x = self.final_norm(x)
        action_logits = self.action_head(x)
        values = self.value_head(x).squeeze(-1)

        result = {
            "action_logits": action_logits,
            "values": values,
        }

        if actions is not None:
            loss = F.cross_entropy(
                action_logits.view(-1, self.config.num_actions),
                actions.view(-1),
            )
            result["loss"] = loss
            predicted = action_logits.argmax(dim=-1)
            result["accuracy"] = (predicted == actions).float().mean()

        return result

    @torch.no_grad()
    def act(
        self,
        obs: torch.Tensor,
        goal_dx: torch.Tensor,
        goal_dy: torch.Tensor,
        timestep: torch.Tensor,
        temperature: float = 0.1,
    ) -> int:
        """Predict a single action for one agent at one timestep."""
        token = self.encode_step(obs, goal_dx, goal_dy, timestep).unsqueeze(1)
        for block in self.transformer:
            token = block(token)
        token = self.final_norm(token)
        logits = self.action_head(token[:, -1]) / max(temperature, 1e-10)
        return torch.multinomial(F.softmax(logits, dim=-1), 1).item()
