import torch
import torch.nn as nn
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp.fully_sharded_data_parallel import CPUOffload, BackwardPrefetch
from torch.distributed.fsdp.wrap import size_based_auto_wrap_policy
import functools
from typing import Tuple, Optional

# OMNI Higgsfield - FSDP Engine
# PyTorch Fully Sharded Data Parallel wrapper with strict error handling

class FSDPEngine:
    def __init__(self, model: nn.Module, device_id: int, min_num_params: int = 1e7):
        self.device_id = device_id
        self.min_num_params = min_num_params
        self.model = model
        self.fsdp_model = None

    def initialize(self) -> Tuple[bool, Optional[Exception]]:
        try:
            # Set auto wrap policy to shard large layers
            my_auto_wrap_policy = functools.partial(
                size_based_auto_wrap_policy, min_num_params=self.min_num_params
            )

            # Initialize FSDP wrapper
            self.fsdp_model = FSDP(
                self.model,
                auto_wrap_policy=my_auto_wrap_policy,
                cpu_offload=CPUOffload(offload_params=True),
                backward_prefetch=BackwardPrefetch.BACKWARD_PRE,
                device_id=self.device_id,
                sync_module_states=True,
            )
            return True, None
        except Exception as e:
            return False, e

    def forward_pass(self, inputs: torch.Tensor) -> Tuple[Optional[torch.Tensor], Optional[Exception]]:
        if self.fsdp_model is None:
            return None, RuntimeError("FSDP Engine not initialized.")
        try:
            outputs = self.fsdp_model(inputs)
            return outputs, None
        except Exception as e:
            return None, e

    def save_checkpoint(self, path: str) -> Tuple[bool, Optional[Exception]]:
        if self.fsdp_model is None:
            return False, RuntimeError("FSDP Engine not initialized.")
        try:
            # Full state dict must be gathered before saving
            with FSDP.state_dict_type(self.fsdp_model, torch.distributed.fsdp.StateDictType.FULL_STATE_DICT):
                state_dict = self.fsdp_model.state_dict()
                if torch.distributed.get_rank() == 0:
                    torch.save(state_dict, path)
            return True, None
        except Exception as e:
            return False, e
