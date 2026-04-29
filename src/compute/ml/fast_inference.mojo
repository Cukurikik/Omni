from tensor import Tensor

fn relu(x: Float32) -> Float32:
    return x if x > 0 else 0.0

fn forward_pass(input: Tensor[DType.float32], weights: Tensor[DType.float32]) raises -> Float32:
    var acc: Float32 = 0.0
    for i in range(input.num_elements()):
        acc += input[i] * weights[i]
    return relu(acc)
