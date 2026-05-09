"""
moe_expert_fusion.py — Expert Fusion and Compression
Layer: Compute / AI — Post-Training Optimization

Fuses highly correlated or functionally identical MoE experts into
a single expert to reduce memory footprint for edge deployment.
Uses weight averaging and cosine similarity mapping.
"""
import torch
import torch.nn as nn
from typing import List, Tuple, Dict


class MoEExpertFusion:
    """Utility to detect and fuse redundant experts."""
    
    @staticmethod
    def calculate_expert_similarity(experts: nn.ModuleList) -> torch.Tensor:
        """
        Calculates cosine similarity between the weight matrices of all experts.
        Returns a (E, E) similarity matrix.
        """
        num_experts = len(experts)
        sim_matrix = torch.zeros((num_experts, num_experts))
        
        with torch.no_grad():
            for i in range(num_experts):
                # Flatten W1 and W2 into a single vector for comparison
                w1_i = experts[i].w1.weight.flatten()
                w2_i = experts[i].w2.weight.flatten()
                vec_i = torch.cat([w1_i, w2_i])
                
                for j in range(i, num_experts):
                    if i == j:
                        sim_matrix[i, j] = 1.0
                        continue
                        
                    w1_j = experts[j].w1.weight.flatten()
                    w2_j = experts[j].w2.weight.flatten()
                    vec_j = torch.cat([w1_j, w2_j])
                    
                    sim = torch.nn.functional.cosine_similarity(vec_i, vec_j, dim=0)
                    sim_matrix[i, j] = sim
                    sim_matrix[j, i] = sim
                    
        return sim_matrix

    @staticmethod
    def identify_fusion_candidates(sim_matrix: torch.Tensor, threshold: float = 0.95) -> List[Tuple[int, int]]:
        """Identifies pairs of experts with similarity above the threshold."""
        num_experts = sim_matrix.shape[0]
        candidates = []
        visited = set()
        
        for i in range(num_experts):
            if i in visited: continue
            for j in range(i + 1, num_experts):
                if j in visited: continue
                
                if sim_matrix[i, j] >= threshold:
                    candidates.append((i, j))
                    visited.add(i)
                    visited.add(j)
                    break # Move to next i
                    
        return candidates

    @staticmethod
    def fuse_experts(expert_a: nn.Module, expert_b: nn.Module) -> nn.Module:
        """
        Creates a new expert by averaging the weights of two experts.
        """
        import copy
        fused = copy.deepcopy(expert_a)
        
        with torch.no_grad():
            fused.w1.weight.copy_((expert_a.w1.weight + expert_b.w1.weight) / 2.0)
            fused.w2.weight.copy_((expert_a.w2.weight + expert_b.w2.weight) / 2.0)
            
            if hasattr(expert_a.w1, 'bias') and expert_a.w1.bias is not None:
                fused.w1.bias.copy_((expert_a.w1.bias + expert_b.w1.bias) / 2.0)
                fused.w2.bias.copy_((expert_a.w2.bias + expert_b.w2.bias) / 2.0)
                
        return fused

    @staticmethod
    def execute_fusion_pass(
        experts: nn.ModuleList, 
        router_gate: nn.Linear, 
        threshold: float = 0.95
    ) -> Tuple[nn.ModuleList, nn.Linear, Dict[int, int]]:
        """
        Executes a full fusion pass: merges experts, updates router weights,
        and returns the new MoE state.
        Returns:
            new_experts, new_router, mapping(old_id -> new_id)
        """
        sim_matrix = MoEExpertFusion.calculate_expert_similarity(experts)
        pairs_to_fuse = MoEExpertFusion.identify_fusion_candidates(sim_matrix, threshold)
        
        if not pairs_to_fuse:
            return experts, router_gate, {i: i for i in range(len(experts))}
            
        dim = router_gate.weight.shape[1]
        old_num_experts = len(experts)
        new_num_experts = old_num_experts - len(pairs_to_fuse)
        
        new_experts = nn.ModuleList()
        new_gate = nn.Linear(dim, new_num_experts, bias=False)
        
        mapping = {}
        new_idx = 0
        fused_sources = set()
        
        # Add fused experts
        with torch.no_grad():
            for a, b in pairs_to_fuse:
                fused_exp = MoEExpertFusion.fuse_experts(experts[a], experts[b])
                new_experts.append(fused_exp)
                
                # Combine routing logits (average)
                new_gate.weight[new_idx] = (router_gate.weight[a] + router_gate.weight[b]) / 2.0
                
                mapping[a] = new_idx
                mapping[b] = new_idx
                fused_sources.add(a)
                fused_sources.add(b)
                new_idx += 1
                
            # Add remaining unfused experts
            for i in range(old_num_experts):
                if i not in fused_sources:
                    new_experts.append(experts[i])
                    new_gate.weight[new_idx] = router_gate.weight[i]
                    mapping[i] = new_idx
                    new_idx += 1
                    
        return new_experts, new_gate, mapping
