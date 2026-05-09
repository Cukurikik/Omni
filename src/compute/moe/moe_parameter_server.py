"""
moe_parameter_server.py — Distributed Expert Weight Server
Layer: Network / AI — MoE Distributed Parameters

A parameter server (PS) designed for large-scale MoE models.
Manages expert weights, serving them to compute nodes on demand,
caching popular experts, and handling gradient aggregation during training.
"""
import torch
import torch.nn as nn
from typing import Dict, List, Tuple
from dataclasses import dataclass
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExpertWeightInfo:
    expert_id: int
    version: int
    size_bytes: int
    access_count: int


class MoEParameterServer:
    """Manages storage and retrieval of MoE expert weights across a cluster."""
    def __init__(self, num_experts: int, dim: int, device: str = "cpu"):
        self.num_experts = num_experts
        self.dim = dim
        self.device = torch.device(device)
        self.lock = threading.RLock()
        
        # Store weights: simple 2-layer MLP for each expert
        self.expert_w1: Dict[int, torch.Tensor] = {}
        self.expert_w2: Dict[int, torch.Tensor] = {}
        
        # Optimizer states
        self.expert_grad_accum: Dict[int, torch.Tensor] = {}
        
        # Metadata
        self.expert_versions = torch.zeros(num_experts, dtype=torch.long)
        self.access_counts = torch.zeros(num_experts, dtype=torch.long)
        
        self._initialize_experts()

    def _initialize_experts(self):
        """Initialize parameters for all experts on the parameter server."""
        for eid in range(self.num_experts):
            # w1: (dim, dim * 4), w2: (dim * 4, dim)
            self.expert_w1[eid] = torch.empty(self.dim, self.dim * 4, device=self.device)
            nn.init.normal_(self.expert_w1[eid], std=0.02)
            
            self.expert_w2[eid] = torch.empty(self.dim * 4, self.dim, device=self.device)
            nn.init.normal_(self.expert_w2[eid], std=0.02)

    def pull_expert(self, expert_id: int) -> Tuple[torch.Tensor, torch.Tensor, int]:
        """Fetch weights for a specific expert (used during forward pass)."""
        with self.lock:
            if expert_id not in self.expert_w1:
                raise ValueError(f"Expert {expert_id} not found on this server.")
            
            self.access_counts[expert_id] += 1
            version = self.expert_versions[expert_id].item()
            
            # Return clones to prevent remote modification of PS memory
            return self.expert_w1[expert_id].clone(), self.expert_w2[expert_id].clone(), version

    def push_gradients(self, expert_id: int, grad_w1: torch.Tensor, grad_w2: torch.Tensor, version: int):
        """Push gradients for an expert (used during backward pass)."""
        with self.lock:
            current_version = self.expert_versions[expert_id].item()
            if version < current_version:
                logger.warning(f"Stale gradient for expert {expert_id}. PS: {current_version}, Grad: {version}")
                # In strict sync mode, we might reject this. For now, accept it.
            
            # Simple SGD update (in production, use Adam/LAMB state here)
            lr = 1e-4
            self.expert_w1[expert_id] -= lr * grad_w1.to(self.device)
            self.expert_w2[expert_id] -= lr * grad_w2.to(self.device)
            
            self.expert_versions[expert_id] += 1

    def get_metadata(self) -> List[ExpertWeightInfo]:
        """Get statistics about expert usage."""
        with self.lock:
            info_list = []
            for eid in range(self.num_experts):
                size = (self.expert_w1[eid].element_size() * self.expert_w1[eid].nelement() +
                        self.expert_w2[eid].element_size() * self.expert_w2[eid].nelement())
                
                info_list.append(ExpertWeightInfo(
                    expert_id=eid,
                    version=self.expert_versions[eid].item(),
                    size_bytes=size,
                    access_count=self.access_counts[eid].item()
                ))
            return info_list

    def save_checkpoint(self, path: str):
        """Serialize PS state to disk."""
        with self.lock:
            state = {
                "w1": self.expert_w1,
                "w2": self.expert_w2,
                "versions": self.expert_versions,
                "access_counts": self.access_counts
            }
            torch.save(state, path)

    def load_checkpoint(self, path: str):
        """Load PS state from disk."""
        with self.lock:
            state = torch.load(path, map_location=self.device)
            self.expert_w1 = state["w1"]
            self.expert_w2 = state["w2"]
            self.expert_versions = state["versions"]
            self.access_counts = state["access_counts"]
