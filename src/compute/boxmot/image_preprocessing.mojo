fn normalize_image(image: Tensor[Float32], mean: Float32, std: Float32) -> Tensor[Float32]:
    let result = Tensor[Float32](image.shape())
    for i in range(image.num_elements()):
        result[i] = (image[i] - mean) / std
    return result
