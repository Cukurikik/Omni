import torch
import triton
import triton.language as tl

@triton.jit
def fused_silu_mul_kernel(
    gate_ptr, up_ptr, out_ptr,
    n_elements,
    BLOCK_SIZE: tl.constexpr,
):
    """
    OMNI Framework - Triton Fused SiLU-Mul Kernel
    Custom OpenAI Triton kernel optimizing the standard SwiGLU / SiLU-gated 
    FFN execution by fusing the activation function and element-wise multiplication
    into a single GPU memory read/write operation. 
    Crucial for accelerating Expert execution in MoE architectures.
    """
    # Identify the thread block
    pid = tl.program_id(axis=0)
    block_start = pid * BLOCK_SIZE
    offsets = block_start + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements

    # Load gate and up vectors from memory
    gate = tl.load(gate_ptr + offsets, mask=mask)
    up = tl.load(up_ptr + offsets, mask=mask)

    # Compute SiLU: x * sigmoid(x)
    # Triton math requires fp32 for precise exp
    gate_fp32 = gate.to(tl.float32)
    sigmoid_gate = 1.0 / (1.0 + tl.exp(-gate_fp32))
    silu_gate = gate_fp32 * sigmoid_gate

    # Multiply by Up projection
    out = silu_gate.to(gate.dtype) * up

    # Store back to memory
    tl.store(out_ptr + offsets, out, mask=mask)

def omni_fused_silu_mul(gate: torch.Tensor, up: torch.Tensor) -> torch.Tensor:
    assert gate.is_cuda and up.is_cuda
    assert gate.shape == up.shape
    
    n_elements = gate.numel()
    out = torch.empty_like(gate)
    
    # Grid specification
    BLOCK_SIZE = 1024
    grid = lambda meta: (triton.cdiv(n_elements, meta['BLOCK_SIZE']), )
    
    fused_silu_mul_kernel[grid](
        gate, up, out,
        n_elements,
        BLOCK_SIZE=BLOCK_SIZE,
    )
    
    return out

# Test
# gate = torch.randn(4096, device='cuda')
# up = torch.randn(4096, device='cuda')
# out = omni_fused_silu_mul(gate, up)
# print("OMNI Triton: Fused SiLU-Mul kernel executed.")
