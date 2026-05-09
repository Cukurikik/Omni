import torch
import torch.nn as nn

# OMNI MOTHER: Expert Gradient Clipper
# Due to sparse gradients in MoE, global norm clipping is often skewed.
# This clips expert parameters independently of dense parameters.

class OmniExpertGradientClipper:
    @staticmethod
    def clip_expert_gradients(model: nn.Module, max_norm: float = 1.0):
        expert_params = []
        dense_params = []
        
        for name, param in model.named_parameters():
            if param.requires_grad:
                if 'expert' in name.lower():
                    expert_params.append(param)
                else:
                    dense_params.append(param)
                    
        # Clip dense globally
        if dense_params:
            torch.nn.utils.clip_grad_norm_(dense_params, max_norm)
            
        # Clip experts individually or as a group
        if expert_params:
            # We clip the expert group separately to prevent dense parameters 
            # from dominating the global norm
            torch.nn.utils.clip_grad_norm_(expert_params, max_norm)
