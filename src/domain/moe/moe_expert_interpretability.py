"""
moe_expert_interpretability.py — Domain / Analytics
Layer: Domain / Data — Expert-Level Interpretability

Inspired by `jerryy33/MoE_analysis`.
MoE networks are notorious "black boxes". This module hooks into the PyTorch
forward pass to intercept the gating network weights and mathematically analyze 
the semantic specialization of each expert over a corpus of text.
"""

import torch
import torch.nn as nn
from typing import Dict, List
from collections import defaultdict

class ExpertInterpretabilityLogger:
    def __init__(self, num_experts: int):
        self.num_experts = num_experts
        # Tracks which tokens were sent to which expert
        self.expert_token_map = defaultdict(list)
        print(f"[Interpretability] Tracking semantic clustering across {num_experts} experts.")

    def hook_routing(self, tokens: List[str], routing_weights: torch.Tensor, top_k: int = 2):
        """
        Called during the forward pass.
        tokens: The string representation of the batch tokens.
        routing_weights: (Seq_Len, Num_Experts)
        """
        seq_len = routing_weights.shape[0]
        
        # Get the top-k expert indices for each token
        topk_weights, topk_indices = torch.topk(routing_weights, top_k, dim=-1)
        
        for i in range(seq_len):
            token_str = tokens[i]
            # Ignore padding or special tokens for interpretability
            if token_str.strip() == "" or token_str.startswith("<"):
                continue
                
            for k in range(top_k):
                expert_id = topk_indices[i, k].item()
                weight = topk_weights[i, k].item()
                
                # Store the token and the confidence weight
                self.expert_token_map[expert_id].append((token_str, weight))

    def generate_report(self) -> Dict[int, List[str]]:
        """
        Analyzes the stored tokens to find the top 10 most highly-weighted
        words for each expert, revealing their semantic specialization.
        """
        report = {}
        for expert_id in range(self.num_experts):
            data = self.expert_token_map[expert_id]
            if not data:
                report[expert_id] = ["(No tokens processed)"]
                continue
                
            # Aggregate weights for identical tokens
            word_scores = defaultdict(float)
            for token, weight in data:
                word_scores[token] += weight
                
            # Sort by total weight descending
            sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Keep top 10
            top_words = [word for word, score in sorted_words[:10]]
            report[expert_id] = top_words
            
        return report

    def clear_cache(self):
        self.expert_token_map.clear()
