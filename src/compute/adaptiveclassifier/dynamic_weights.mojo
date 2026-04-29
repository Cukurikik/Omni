struct OmniResult[T: AnyType]:
    var value: T
    var error: String
    var is_ok: Bool

fn update_dynamic_weights(weights: Tensor[DType.float32], gradient: Tensor[DType.float32], lr: Float32) -> OmniResult[Tensor[DType.float32]]:
    if weights.num_elements() != gradient.num_elements():
        return OmniResult[Tensor[DType.float32]](weights, "Shape mismatch between weights and gradients", False)

    # Mojo SIMD accelerated weight updates for Adaptive Classifier
    var updated_weights = Tensor[DType.float32](weights.shape())
    for i in range(weights.num_elements()):
        updated_weights[i] = weights[i] - (lr * gradient[i])

    return OmniResult[Tensor[DType.float32]](updated_weights, "", True)
