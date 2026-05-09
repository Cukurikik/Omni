"""
moe_quant_calibration.py — Compute / Optimization
Layer: Compute / AI — Post-Training Quantization (PTQ) Calibration

When quantizing an MoE model from FP16 to INT8, precision drops. 
This script runs a "Calibration" loop: it pushes a small dataset of real data
through the network to calculate the actual min/max activation ranges. 
These ranges are used to compute optimal quantization scales.
"""
import torch
import torch.nn as nn
from typing import List

class MinMaxCalibrator:
    """Tracks activation statistics during calibration."""
    def __init__(self):
        self.min_val = float('inf')
        self.max_val = float('-inf')

    def update(self, tensor: torch.Tensor):
        current_min = tensor.min().item()
        current_max = tensor.max().item()
        
        if current_min < self.min_val: self.min_val = current_min
        if current_max > self.max_val: self.max_val = current_max

class MoEPTQCalibrator:
    """
    Calibrates an MoE model for static Post-Training Quantization.
    """
    def __init__(self, model: nn.Module):
        self.model = model
        self.expert_stats = {}
        
        # Attach hooks to linear layers within experts
        self._attach_hooks()
        print("[MoE PTQ] Attached activation calibration hooks.")

    def _attach_hooks(self):
        def get_hook(name):
            def hook(module, input, output):
                if name not in self.expert_stats:
                    self.expert_stats[name] = MinMaxCalibrator()
                # input[0] is the activation tensor going into the linear layer
                self.expert_stats[name].update(input[0])
            return hook

        # Recursively find experts and attach hooks
        for name, module in self.model.named_modules():
            if "experts" in name and isinstance(module, nn.Linear):
                module.register_forward_hook(get_hook(name))

    def calibrate(self, calibration_dataloader: List[torch.Tensor]):
        """
        Runs the model in inference mode to gather activation stats.
        """
        print(f"[MoE PTQ] Starting calibration over {len(calibration_dataloader)} batches...")
        self.model.eval()
        
        with torch.no_grad():
            for batch in calibration_dataloader:
                _ = self.model(batch)
                
        print("[MoE PTQ] Calibration complete. Calculating scales.")
        return self._compute_scales()

    def _compute_scales(self) -> dict:
        """
        Calculates the FP32 -> INT8 scaling factors based on symmetric quantization.
        scale = max(|min|, |max|) / 127
        """
        scales = {}
        for name, calib in self.expert_stats.items():
            abs_max = max(abs(calib.min_val), abs(calib.max_val))
            scale = abs_max / 127.0 if abs_max > 0 else 1.0
            scales[name] = scale
            
        return scales
