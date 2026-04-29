struct OmniResult[T: AnyType]:
    var value: T
    var error: String
    var is_ok: Bool

fn decode_logits(logits: Tensor[DType.float32]) -> OmniResult[Int]:
    if logits.num_elements() == 0:
        return OmniResult[Int](0, "Empty logits", False)

    # Mojo SIMD accelerated argmax for text decoding in LLaVA-Mini
    var max_idx = 0
    var max_val = logits[0]
    for i in range(1, logits.num_elements()):
        if logits[i] > max_val:
            max_val = logits[i]
            max_idx = i

    return OmniResult[Int](max_idx, "", True)
