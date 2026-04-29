import torch
import torch.nn as nn
from typing import List, Tuple, Any

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error

    @classmethod
    def ok(cls, value: Any):
        return cls(True, value=value)

    @classmethod
    def err(cls, error: str):
        return cls(False, error=error)

class AdaNetEnsemble(nn.Module):
    def __init__(self, input_dim: int, num_classes: int):
        super().__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.subnetworks = nn.ModuleList()
        # Learnable mixture weights per subnetwork
        self.mixture_weights = nn.ParameterList()
        
    def add_subnetwork(self, network: nn.Module) -> OmniResult:
        try:
            # Validate output matches
            dummy_input = torch.randn(1, self.input_dim)
            out = network(dummy_input)
            if out.shape[-1] != self.num_classes:
                return OmniResult.err(f"Subnetwork output dim {out.shape[-1]} != {self.num_classes}")
                
            self.subnetworks.append(network)
            # Initialize new weight
            weight = nn.Parameter(torch.tensor(1.0 / len(self.subnetworks)))
            self.mixture_weights.append(weight)
            return OmniResult.ok(len(self.subnetworks))
        except Exception as e:
            return OmniResult.err(f"Failed to add subnetwork: {str(e)}")

    def forward(self, x: torch.Tensor) -> OmniResult:
        if len(self.subnetworks) == 0:
            return OmniResult.err("Ensemble has no subnetworks")
            
        try:
            outputs = []
            for net in self.subnetworks:
                outputs.append(net(x))
                
            stacked_outputs = torch.stack(outputs, dim=0) # [num_nets, batch, classes]
            
            # Normalize weights using softmax
            weights = torch.stack([w for w in self.mixture_weights])
            normalized_weights = torch.softmax(weights, dim=0)
            
            # Weighted sum
            # view for broadcasting: [num_nets, 1, 1]
            weighted_outputs = stacked_outputs * normalized_weights.view(-1, 1, 1)
            ensemble_output = torch.sum(weighted_outputs, dim=0)
            
            return OmniResult.ok(ensemble_output)
        except Exception as e:
            return OmniResult.err(f"Ensemble forward pass failed: {str(e)}")

    def get_complexity_penalty(self, lambda_val: float) -> OmniResult:
        try:
            # AdaNet objective penalty: lambda * sum(|w_i| * complexity(net_i))
            penalty = torch.tensor(0.0, device=self.mixture_weights[0].device)
            for w, net in zip(self.mixture_weights, self.subnetworks):
                # Simple complexity metric: number of parameters
                complexity = sum(p.numel() for p in net.parameters())
                penalty += torch.abs(w) * complexity * lambda_val
            return OmniResult.ok(penalty)
        except Exception as e:
            return OmniResult.err(f"Penalty calculation failed: {str(e)}")
