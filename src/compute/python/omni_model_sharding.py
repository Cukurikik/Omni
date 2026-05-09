import torch

# OMNI MOTHER: MoE Expert Sharding (Production Grade)
# Distributes experts across nodes (Expert Parallelism).

class OmniExpertSharder:
    def __init__(self, total_experts: int, world_size: int, rank: int):
        self.total_experts = total_experts
        self.world_size = world_size
        self.rank = rank
        
        # Experts handled by this specific GPU
        self.local_experts_range = (
            (total_experts // world_size) * rank,
            (total_experts // world_size) * (rank + 1)
        )

    def is_local(self, expert_id: int) -> bool:
        start, end = self.local_experts_range
        return start <= expert_id < end
        
    def print_status(self):
        print(f"[OMNI SHARDER] Node {self.rank} managing experts {self.local_experts_range[0]} to {self.local_experts_range[1]-1}")
