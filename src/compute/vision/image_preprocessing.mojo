from tensor import Tensor

fn normalize_image(image: Tensor[DType.float32]) raises -> Tensor[DType.float32]:
    let out = Tensor[DType.float32](image.shape())
    for i in range(image.num_elements()):
        out[i] = image[i] / 255.0
    return out
