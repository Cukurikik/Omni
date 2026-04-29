struct OmniResult[T: AnyType, E: StringType]:
    var is_ok: Bool; var value: T; var error: E
    fn __init__(inout self, value: T): self.is_ok = True; self.value = value; self.error = ""
    fn __init__(inout self, error: E): self.is_ok = False; self.error = error

fn compute_adapter_merge(base_weight: Float64, lora_delta: Float64, alpha: Float64, rank: Float64) -> OmniResult[Float64, String]:
    if rank <= 0.0:
        return OmniResult[Float64, String](error="Rank must be positive")
    if alpha < 0.0 or alpha > 1000.0:
        return OmniResult[Float64, String](error="Alpha out of bounds")
    var scale = alpha / rank
    var merged = base_weight + scale * lora_delta
    return OmniResult[Float64, String](value=merged)
