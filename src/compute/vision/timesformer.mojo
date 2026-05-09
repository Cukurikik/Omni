#=============================================================================
# OMNI COMPUTE LAYER — TIMESFORMER VIDEO CLASSIFICATION (MOJO)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Divided Space-Time Attention for Video Understanding.
# INSPIRED BY: davide-coccomini/TimeSformer-Video-Classification
#=============================================================================

from tensor import Tensor
from utils.index import Index
import omni_bridge.system.memory as memory

@value
struct SpaceTimeAttention(mojo::accelerate):
    var embed_dim: Int
    var num_heads: Int
    var frames: Int
    var patches: Int
    
    fn __init__(inout self, embed_dim: Int, num_heads: Int, frames: Int, patches: Int):
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.frames = frames
        self.patches = patches
        
    fn forward(self, x: Tensor[DType.float32]) -> Tensor[DType.float32]:
        """
        Applies Temporal Attention followed by Spatial Attention.
        x shape: [Batch, Frames * Patches, Embed_Dim]
        """
        # Step 1: Temporal Attention
        let temp_out = self.temporal_attention(x)
        
        # Step 2: Spatial Attention
        let spatial_out = self.spatial_attention(temp_out)
        
        return spatial_out
        
    fn temporal_attention(self, x: Tensor[DType.float32]) -> Tensor[DType.float32]:
        # Delegate to high-performance C++ backend via Omni bridge
        var output = Tensor[DType.float32](x.shape())
        let in_ptr = memory::get_raw_pointer(x)
        let out_ptr = memory::get_raw_pointer(output)
        
        memory::omni_c_execute_temporal_attn(in_ptr, out_ptr, self.frames, self.patches, self.embed_dim)
        return output
        
    fn spatial_attention(self, x: Tensor[DType.float32]) -> Tensor[DType.float32]:
        # Delegate to high-performance C++ backend via Omni bridge
        var output = Tensor[DType.float32](x.shape())
        let in_ptr = memory::get_raw_pointer(x)
        let out_ptr = memory::get_raw_pointer(output)
        
        memory::omni_c_execute_spatial_attn(in_ptr, out_ptr, self.frames, self.patches, self.embed_dim)
        return output

