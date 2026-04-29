# Omni MMStar Vision Eval (Mojo)
# Based on MMStar-Benchmark/MMStar
# Fast evaluation of Large Vision-Language Models.

from tensor import Tensor

struct OmniMMStarEvaluator:
    var dims: Int

    fn __init__(inout self, dims: Int):
        self.dims = dims
        
    fn compute_vision_language_alignment(self, img_feat: Tensor[DType.float32], txt_feat: Tensor[DType.float32]) raises -> Float32:
        if img_feat.num_elements() != self.dims or txt_feat.num_elements() != self.dims:
            raise Error("Dimension mismatch in MMStar")
            
        var alignment_score: Float32 = 0.0
        for i in range(self.dims):
            alignment_score += img_feat[i] * txt_feat[i]
            
        return alignment_score

fn run_mmstar_eval(img: Tensor[DType.float32], txt: Tensor[DType.float32]) -> Float32:
    try:
        var engine = OmniMMStarEvaluator(img.num_elements())
        return engine.compute_vision_language_alignment(img, txt)
    except:
        return -1.0
