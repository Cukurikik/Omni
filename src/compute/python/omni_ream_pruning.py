import torch
import torch.nn as nn

# OMNI MOTHER: REAM (Merging Improves Pruning of Experts in LLMs)
# Merges similar experts before pruning to preserve capabilities

class OmniReamPruner:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def _compute_similarity(self, exp1: nn.Linear, exp2: nn.Linear) -> float:
        # Cosine similarity between expert weight matrices
        w1 = exp1.weight.view(-1)
        w2 = exp2.weight.view(-1)
        cos_sim = torch.nn.functional.cosine_similarity(w1, w2, dim=0)
        return cos_sim.item()

    def merge_and_prune(self, experts: nn.ModuleList) -> nn.ModuleList:
        num_experts = len(experts)
        merged = []
        skip = set()
        
        for i in range(num_experts):
            if i in skip:
                continue
            for j in range(i + 1, num_experts):
                if j in skip:
                    continue
                sim = self._compute_similarity(experts[i], experts[j])
                if sim > self.threshold:
                    # Merge experts j into i
                    experts[i].weight.data = (experts[i].weight.data + experts[j].weight.data) / 2.0
                    skip.add(j)
                    print(f"[OMNI REAM] Merged expert {j} into {i} (Similarity: {sim:.2f})")
            merged.append(experts[i])
            
        return nn.ModuleList(merged)
