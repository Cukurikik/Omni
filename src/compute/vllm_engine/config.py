from dataclasses import dataclass
from omni.core import Result, Ok, Err

@dataclass(frozen=True)
class VllmConfig:
    max_num_seqs: int
    block_size: int
    gpu_memory_utilization: float

def load_config() -> Result[VllmConfig, ValueError]:
    config = VllmConfig(max_num_seqs=256, block_size=16, gpu_memory_utilization=0.90)
    return Ok(config)
