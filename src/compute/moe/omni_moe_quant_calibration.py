import torch
import torch.nn as nn

# OMNI MOTHER Production Zero-Mock Quantization Calibration
# Calibrates dynamic scaling factors for INT8/FP8 quantization of MoE experts
# by analyzing activation statistics during a calibration pass.

class ActivationCalibrator:
    def __init__(self, method='absmax'):
        self.method = method
        self.activation_stats = {}
        self.hooks = []

    def attach(self, model: nn.Module):
        for name, module in model.named_modules():
            if isinstance(module, (nn.Linear, nn.Conv1d, nn.Conv2d)):
                hook = module.register_forward_hook(self._get_hook(name))
                self.hooks.append(hook)

    def _get_hook(self, name: str):
        def hook(module, input, output):
            tensor = input[0].detach()
            
            if name not in self.activation_stats:
                self.activation_stats[name] = {
                    'max': tensor.max().item(),
                    'min': tensor.min().item(),
                    'absmax': tensor.abs().max().item()
                }
            else:
                stats = self.activation_stats[name]
                stats['max'] = max(stats['max'], tensor.max().item())
                stats['min'] = min(stats['min'], tensor.min().item())
                stats['absmax'] = max(stats['absmax'], tensor.abs().max().item())
                
        return hook

    def detach(self):
        for hook in self.hooks:
            hook.remove()
        self.hooks = []

    def compute_scales(self, num_bits=8):
        scales = {}
        qmin = -(2 ** (num_bits - 1))
        qmax = (2 ** (num_bits - 1)) - 1
        
        for name, stats in self.activation_stats.items():
            if self.method == 'absmax':
                # Symmetric quantization
                scale = stats['absmax'] / qmax
            elif self.method == 'minmax':
                # Asymmetric quantization
                scale = (stats['max'] - stats['min']) / (qmax - qmin)
            else:
                raise ValueError(f"OMNI CRITICAL: Unknown calibration method {self.method}")
                
            # Prevent div-by-zero
            scales[name] = max(scale, 1e-8)
            
        return scales
