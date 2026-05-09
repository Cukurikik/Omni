"""OMNI Compute — Tensor Parallel Inference Manager"""
import logging; from dataclasses import dataclass; from typing import Dict, List
logger = logging.getLogger("omni.tp")
@dataclass  
class TPConfig:
    world_size: int = 4; pipeline_stages: int = 1
    communication: str = "nccl"  # nccl | gloo
class TensorParallelManager:
    """Manages tensor and pipeline parallelism for multi-GPU inference."""
    def __init__(self, c: TPConfig): self.config = c
    def compute_shard_plan(self, model_config: Dict) -> Dict:
        dim = model_config.get("hidden_dim", 4096); heads = model_config.get("num_heads", 32)
        ffn = model_config.get("ffn_dim", 11008); layers = model_config.get("num_layers", 32)
        ws = self.config.world_size
        return {"qkv_shard_dim": dim // ws, "heads_per_gpu": heads // ws,
                "ffn_shard_dim": ffn // ws, "layers_per_stage": layers // max(self.config.pipeline_stages, 1),
                "vocab_shard": True, "embedding_replicated": True}
    def estimate_memory(self, params_billions: float) -> Dict:
        ws = self.config.world_size
        total_gb = params_billions * 2  # fp16
        per_gpu = total_gb / ws
        kv_cache_per_gpu = 2  # rough estimate GB
        return {"total_model_gb": total_gb, "per_gpu_gb": round(per_gpu, 2),
                "kv_cache_gb": kv_cache_per_gpu, "total_per_gpu_gb": round(per_gpu + kv_cache_per_gpu, 2),
                "min_gpu_memory_gb": round((per_gpu + kv_cache_per_gpu) * 1.2, 1)}
    def info(self) -> Dict:
        return {"world_size": self.config.world_size, "pipeline_stages": self.config.pipeline_stages,
                "communication": self.config.communication}
