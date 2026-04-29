fn fast_sigmoid(x: Float32) -> Float32:
    return 1.0 / (1.0 + math.exp(-x))

fn process_box(box: Tensor[Float32]) -> Tensor[Float32]:
    # Mojo SIMD accelerated box processing
    let result = Tensor[Float32](box.shape())
    for i in range(box.num_elements()):
        result[i] = fast_sigmoid(box[i])
    return result
