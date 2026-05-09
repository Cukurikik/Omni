#=============================================================================
# OMNI COMPUTE LAYER — DIFFERENTIAL ATTENTION (MOJO)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Core Differential Attention algorithm implementation in Mojo.
#              Delegates raw GEMM to CUDA kernels via pointers.
#=============================================================================

from tensor import Tensor
import omni_bridge.system.memory as memory

@value
struct DiffAttention(mojo::accelerate):
    var embed_dim: Int
    var num_heads: Int
    var lambda_val: Float32
    
    fn __init__(inout self, embed_dim: Int, num_heads: Int, lambda_val: Float32 = 0.8):
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.lambda_val = lambda_val
        
    fn forward(self, q1: Tensor[DType.float32], k1: Tensor[DType.float32], v1: Tensor[DType.float32],
                     q2: Tensor[DType.float32], k2: Tensor[DType.float32], v2: Tensor[DType.float32]) -> Tensor[DType.float32]:
        """
        Computes Diff = Attention(q1, k1, v1) - lambda * Attention(q2, k2, v2)
        """
        let batch = q1.dim(0)
        let seq = q1.dim(1)
        
        var attn1_out = Tensor[DType.float32](batch, seq, self.embed_dim)
        var attn2_out = Tensor[DType.float32](batch, seq, self.embed_dim)
        
        # 1. Execute Attention 1 (C++ / CUDA Kernel)
        memory::omni_cuda_attention(
            memory::get_raw_pointer(q1), memory::get_raw_pointer(k1), memory::get_raw_pointer(v1),
            memory::get_raw_pointer(attn1_out), batch, self.num_heads, seq, self.embed_dim // self.num_heads, 1.0
        )
        
        # 2. Execute Attention 2
        memory::omni_cuda_attention(
            memory::get_raw_pointer(q2), memory::get_raw_pointer(k2), memory::get_raw_pointer(v2),
            memory::get_raw_pointer(attn2_out), batch, self.num_heads, seq, self.embed_dim // self.num_heads, 1.0
        )
        
        # 3. Compute Differential (SIMD subtract and scale)
        # diff_out = attn1_out - (lambda * attn2_out)
        var diff_out = Tensor[DType.float32](batch, seq, self.embed_dim)
        memory::omni_c_simd_diff_attention(
            memory::get_raw_pointer(attn1_out), memory::get_raw_pointer(attn2_out), 
            memory::get_raw_pointer(diff_out), diff_out.num_elements(), self.lambda_val
        )
        
        return diff_out
