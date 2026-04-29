from tensor import Tensor

fn dot_product(a: Tensor[DType.float32], b: Tensor[DType.float32]) raises -> Float32:
    if a.num_elements() != b.num_elements():
        raise Error("Dimension mismatch in dot product")
    
    var sum: Float32 = 0.0
    for i in range(a.num_elements()):
        sum += a[i] * b[i]
    return sum
