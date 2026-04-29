import torch

def compress_gradients(grads: torch.Tensor, rank: int) -> torch.Tensor:
    """Flora: Low-Rank Adapters Are Secretly Gradient Compressors"""
    if grads.dim() != 2:
        return grads
    
    U, S, V = torch.svd_lowrank(grads, q=rank)
    compressed = U @ torch.diag(S) @ V.T
    return compressed
