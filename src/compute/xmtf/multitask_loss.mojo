struct OmniResult[T: AnyType]:
    var value: T
    var error: String
    var is_ok: Bool

fn compute_multitask_loss(predictions: Tensor[DType.float32], targets: Tensor[DType.float32]) -> OmniResult[Float32]:
    if predictions.num_elements() != targets.num_elements():
        return OmniResult[Float32](0.0, "Shape mismatch", False)

    # Mojo SIMD accelerated MSE loss for xMTF
    var loss: Float32 = 0.0
    for i in range(predictions.num_elements()):
        var diff = predictions[i] - targets[i]
        loss += diff * diff
        
    loss = loss / predictions.num_elements()

    return OmniResult[Float32](loss, "", True)
