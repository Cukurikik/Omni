import torch
import os

# OMNI MOTHER: Distributed Checkpointing
# Saves expert weights individually for huge MoE models

class OmniMoECheckpointer:
    def __init__(self, save_dir: str):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def save_expert(self, expert_idx: int, state_dict: dict):
        path = os.path.join(self.save_dir, f"expert_{expert_idx}.pt")
        torch.save(state_dict, path)
        print(f"[OMNI] Saved expert {expert_idx} to {path}")
