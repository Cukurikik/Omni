"""
moe_expert_parallel.py — Expert Parallelism Communication Primitives
Reference: TorchTitan/PyTorch expert parallelism, Megatron-LM EP
Layer: Compute / AI — MoE Distributed

Implements all-to-all token dispatch and gather for expert parallelism.
Each rank hosts a subset of experts; tokens are dispatched to the
appropriate rank, processed by local experts, then gathered back.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.distributed as dist
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class EPConfig:
    num_experts: int = 64
    world_size: int = 8
    top_k: int = 2
    capacity_factor: float = 1.25
    comm_backend: str = "nccl"


def get_expert_range(rank: int, num_experts: int, world_size: int) -> Tuple[int, int]:
    """Get the expert ID range [start, end) for a given rank."""
    per_rank = num_experts // world_size
    start = rank * per_rank
    end = start + per_rank
    return start, end


class TokenDispatchInfo:
    """Stores dispatch metadata for all-to-all communication."""
    def __init__(self, num_tokens: int, top_k: int, num_experts: int, world_size: int):
        self.send_counts = torch.zeros(world_size, dtype=torch.long)
        self.recv_counts = torch.zeros(world_size, dtype=torch.long)
        self.token_to_rank = torch.zeros(num_tokens * top_k, dtype=torch.long)
        self.local_expert_offset = torch.zeros(num_experts, dtype=torch.long)


def compute_dispatch_info(
    expert_indices: torch.Tensor,
    num_experts: int,
    world_size: int,
) -> TokenDispatchInfo:
    """Compute dispatch routing from expert assignments."""
    N, K = expert_indices.shape
    info = TokenDispatchInfo(N, K, num_experts, world_size)
    experts_per_rank = num_experts // world_size

    for i in range(N):
        for k in range(K):
            eid = expert_indices[i, k].item()
            rank = min(eid // experts_per_rank, world_size - 1)
            info.send_counts[rank] += 1
            info.token_to_rank[i * K + k] = rank

    return info


class AllToAllDispatcher(nn.Module):
    """Dispatches tokens across ranks for expert parallelism."""
    def __init__(self, config: EPConfig):
        super().__init__()
        self.config = config
        self.experts_per_rank = config.num_experts // config.world_size

    def forward(
        self,
        tokens: torch.Tensor,
        expert_indices: torch.Tensor,
        expert_weights: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, TokenDispatchInfo]:
        """Dispatch tokens to expert-owning ranks.

        For single-GPU / non-distributed: acts as identity with reordering.
        For distributed: performs all-to-all communication.
        """
        N, D = tokens.shape
        K = expert_indices.shape[1]
        info = compute_dispatch_info(
            expert_indices, self.config.num_experts, self.config.world_size)

        if not dist.is_initialized() or self.config.world_size <= 1:
            # Non-distributed: just sort by expert
            sort_idx = expert_indices[:, 0].argsort()
            return tokens[sort_idx], expert_indices[sort_idx], expert_weights[sort_idx], info

        # Exchange send/recv counts
        dist.all_to_all_single(info.recv_counts, info.send_counts)

        # Prepare send buffers sorted by destination rank
        total_send = info.send_counts.sum().item()
        send_buf = torch.zeros(total_send, D, device=tokens.device, dtype=tokens.dtype)
        send_idx_buf = torch.zeros(total_send, K, device=expert_indices.device,
                                    dtype=expert_indices.dtype)
        send_w_buf = torch.zeros(total_send, K, device=expert_weights.device,
                                  dtype=expert_weights.dtype)

        # Sort tokens by destination rank
        offsets = torch.zeros(self.config.world_size, dtype=torch.long)
        for r in range(1, self.config.world_size):
            offsets[r] = offsets[r-1] + info.send_counts[r-1]

        write_pos = offsets.clone()
        for i in range(N):
            rank = info.token_to_rank[i * K].item()
            pos = write_pos[rank].item()
            send_buf[pos] = tokens[i]
            send_idx_buf[pos] = expert_indices[i]
            send_w_buf[pos] = expert_weights[i]
            write_pos[rank] += 1

        # All-to-all data exchange
        total_recv = info.recv_counts.sum().item()
        recv_buf = torch.zeros(total_recv, D, device=tokens.device, dtype=tokens.dtype)

        send_splits = info.send_counts.tolist()
        recv_splits = info.recv_counts.tolist()

        dist.all_to_all(
            [recv_buf[sum(recv_splits[:r]):sum(recv_splits[:r+1])]
             for r in range(self.config.world_size)],
            [send_buf[sum(send_splits[:r]):sum(send_splits[:r+1])]
             for r in range(self.config.world_size)],
        )

        return recv_buf, send_idx_buf, send_w_buf, info


class AllToAllGatherer(nn.Module):
    """Gathers expert outputs back to the originating ranks."""
    def __init__(self, config: EPConfig):
        super().__init__()
        self.config = config

    def forward(
        self,
        expert_outputs: torch.Tensor,
        dispatch_info: TokenDispatchInfo,
        original_shape: Tuple[int, int],
    ) -> torch.Tensor:
        """Gather expert outputs back to originating tokens."""
        N, D = original_shape

        if not dist.is_initialized() or self.config.world_size <= 1:
            return expert_outputs

        # Reverse all-to-all: send expert_outputs back
        send_splits = dispatch_info.recv_counts.tolist()
        recv_splits = dispatch_info.send_counts.tolist()

        total_recv = sum(recv_splits)
        recv_buf = torch.zeros(total_recv, D, device=expert_outputs.device,
                               dtype=expert_outputs.dtype)

        dist.all_to_all(
            [recv_buf[sum(recv_splits[:r]):sum(recv_splits[:r+1])]
             for r in range(self.config.world_size)],
            [expert_outputs[sum(send_splits[:r]):sum(send_splits[:r+1])]
             for r in range(self.config.world_size)],
        )

        return recv_buf


class MoEExpertParallelLayer(nn.Module):
    """Full MoE layer with expert parallelism support."""
    def __init__(self, dim, config: EPConfig):
        super().__init__()
        self.config = config
        self.dispatcher = AllToAllDispatcher(config)
        self.gatherer = AllToAllGatherer(config)

        # Gate for all experts (each rank computes full routing)
        self.gate = nn.Linear(dim, config.num_experts, bias=False)

        # Only instantiate local experts
        rank = dist.get_rank() if dist.is_initialized() else 0
        start, end = get_expert_range(rank, config.num_experts, config.world_size)
        self.local_experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(dim, dim * 4, bias=False),
                nn.SiLU(),
                nn.Linear(dim * 4, dim, bias=False),
            )
            for _ in range(end - start)
        ])
        self.local_start = start
        self.local_end = end
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> dict:
        B, S, D = x.shape
        residual = x
        flat = self.norm(x).reshape(-1, D)
        N = flat.shape[0]

        # Compute routing
        logits = self.gate(flat)
        probs = F.softmax(logits, dim=-1)
        topk_w, topk_idx = torch.topk(probs, self.config.top_k, dim=-1)
        topk_w = topk_w / topk_w.sum(dim=-1, keepdim=True).clamp(min=1e-8)

        # Dispatch
        dispatched, d_idx, d_w, info = self.dispatcher(flat, topk_idx, topk_w)

        # Process local experts
        output = torch.zeros_like(dispatched)
        for i, expert in enumerate(self.local_experts):
            eid = self.local_start + i
            mask = (d_idx == eid).any(dim=-1)
            if mask.any():
                tok_idx = mask.nonzero(as_tuple=True)[0]
                e_out = expert(dispatched[tok_idx])
                for k in range(self.config.top_k):
                    km = d_idx[tok_idx, k] == eid
                    if km.any():
                        ki = tok_idx[km]
                        output[ki] += e_out[km] * d_w[ki, k].unsqueeze(-1)

        # Gather
        gathered = self.gatherer(output, info, (N, D))
        result = gathered.reshape(B, S, D) + residual

        # Aux loss
        f = F.one_hot(topk_idx[:, 0], self.config.num_experts).float().mean(0)
        p = probs.mean(0)
        aux = (f * p).sum() * self.config.num_experts * 0.01

        return {"output": result, "aux_loss": aux}
