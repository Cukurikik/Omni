# OMNI Compute Layer - PyTorch Custom Autograd
import torch

class AutogradError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

class OmniCustomOp(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, w):
        ctx.save_for_backward(x, w)
        return x.mm(w)

    @staticmethod
    def backward(ctx, grad_output):
        x, w = ctx.saved_tensors
        grad_x = grad_output.mm(w.t())
        grad_w = x.t().mm(grad_output)
        return grad_x, grad_w

def apply_custom_autograd(x: torch.Tensor, w: torch.Tensor) -> Result:
    """Applies an optimized custom autograd function."""
    try:
        if x.dim() != 2 or w.dim() != 2:
            return Result(error=AutogradError("Tensors must be 2D"))
            
        out = OmniCustomOp.apply(x, w)
        return Result(value={"output_tensor": out})
    except Exception as e:
        return Result(error=AutogradError(f"Autograd failed: {str(e)}"))
