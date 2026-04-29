fn attention_scores(query: Tensor[Float32], key: Tensor[Float32], scale: Float32) -> Tensor[Float32]:
    # Mojo optimized attention calculation
    let transposed_k = key.transpose()
    let raw_scores = query.matmul(transposed_k)
    # Apply scaling
    for i in range(raw_scores.size):
        raw_scores[i] = raw_scores[i] * scale
    return raw_scores
