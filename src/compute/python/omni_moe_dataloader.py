from torch.utils.data import DataLoader
from .omni_moe_dataset import OmniMoEDataset

# OMNI MOTHER: MoE Dataloader
# Configured for high-throughput GPU feeding

def create_omni_dataloader(token_file: str, batch_size: int, num_workers: int = 4):
    dataset = OmniMoEDataset(token_file)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        prefetch_factor=2
    )
    return loader
