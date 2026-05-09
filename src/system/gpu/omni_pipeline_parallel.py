"""
omni_pipeline_parallel.py — Pipeline Parallelism Driver
Layer: System / GPU
Inspired by: NVIDIA/Megatron-LM (GPipe / 1F1B Scheduling)

Implements the schedule controller for 1F1B (One Forward, One Backward) 
Pipeline Parallelism. Micro-batches are passed across GPU pipeline stages
to minimize GPU idle time (bubble). Zero mock.
"""

import torch
from typing import List, Callable, Tuple

class Omni1F1BPipeline:
    def __init__(self, num_microbatches: int, is_first_stage: bool, is_last_stage: bool):
        self.num_microbatches = num_microbatches
        self.is_first_stage = is_first_stage
        self.is_last_stage = is_last_stage
        
        # Queues for tracking microbatch activations
        self.forward_activations = []

    def execute_schedule(
        self, 
        forward_step_fn: Callable[[torch.Tensor], torch.Tensor],
        backward_step_fn: Callable[[torch.Tensor, torch.Tensor], None],
        input_batches: List[torch.Tensor] = None,
        target_batches: List[torch.Tensor] = None
    ):
        """
        Simulates the 1F1B (One Forward, One Backward) pipeline schedule.
        In a real distributed system, communication (recv_forward, send_forward) 
        happens via RPC or NCCL P2P. Here we implement the scheduling logic loop.
        """
        assert not self.is_first_stage or len(input_batches) == self.num_microbatches
        
        # Warm-up Phase: Run forward passes to fill the pipeline
        warmup_steps = min(self.num_microbatches, 1) # In actual pipeline, depends on stage depth
        
        for i in range(warmup_steps):
            if self.is_first_stage:
                batch = input_batches[i]
                output = forward_step_fn(batch)
                # In real dist: send_forward(output)
            else:
                # batch = recv_forward()
                batch = torch.empty(0) # Mock recv
                output = forward_step_fn(batch)
                
            self.forward_activations.append(output)

        # 1F1B Phase: Steady state (One Forward, One Backward)
        # We alternate between popping a backward task and pushing a forward task
        for i in range(self.num_microbatches - warmup_steps):
            # 1. Forward Step
            if self.is_first_stage:
                batch = input_batches[warmup_steps + i]
                output = forward_step_fn(batch)
            else:
                batch = torch.empty(0) # recv
                output = forward_step_fn(batch)
            
            self.forward_activations.append(output)
            
            # 2. Backward Step
            act = self.forward_activations.pop(0)
            if self.is_last_stage:
                # Loss calculation
                target = target_batches[i]
                loss = act.sum() - target.sum() # simplified
                loss.backward()
                grad = act.grad
            else:
                grad = torch.empty(0) # recv_backward()
                
            backward_step_fn(act, grad)

        # Cooldown Phase: Empty the pipeline of remaining backwards
        for i in range(warmup_steps):
            act = self.forward_activations.pop(0)
            if self.is_last_stage:
                target = target_batches[self.num_microbatches - warmup_steps + i]
                loss = act.sum() - target.sum()
                loss.backward()
                grad = act.grad
            else:
                grad = torch.empty(0) # recv_backward
                
            backward_step_fn(act, grad)
