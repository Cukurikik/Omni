struct OmniResult[T: AnyType]:
    var value: T
    var error: String
    var is_ok: Bool

fn score_html_content(content_vector: Tensor[DType.float32]) -> OmniResult[Float32]:
    if content_vector.num_elements() == 0:
        return OmniResult[Float32](0.0, "Empty content", False)

    # Mojo accelerated text density scoring for Craw4LLM
    var sum_density: Float32 = 0.0
    for i in range(content_vector.num_elements()):
        sum_density += content_vector[i] * 0.8
        
    return OmniResult[Float32](sum_density / Float32(content_vector.num_elements()), "", True)
