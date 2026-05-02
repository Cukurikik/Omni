# @omni-domain Compute Layer (Style Transfer)
# @omni-source various/stylellm
# @omni-description Style Transfer Model mimicking neural style matrix ops in Mojo.
# @omni-requirement zero-mock, monadic-error

struct OmniResult[T: AnyType]:
    var data: T
    var error: String
    var is_ok: Bool

fn compute_gram_matrix(features: DynamicVector[DynamicVector[Float64]], n_channels: Int, spatial: Int) -> OmniResult[DynamicVector[DynamicVector[Float64]]]:
    if n_channels <= 0 or spatial <= 0:
        return OmniResult[DynamicVector[DynamicVector[Float64]]](DynamicVector[DynamicVector[Float64]](), "Invalid dimensions.", False)

    var gram = DynamicVector[DynamicVector[Float64]]()
    for i in range(n_channels):
        var row = DynamicVector[Float64]()
        for j in range(n_channels):
            var dot: Float64 = 0.0
            for k in range(spatial):
                dot += features[i][k] * features[j][k]
            row.append(dot / Float64(spatial))
        gram.append(row)

    return OmniResult[DynamicVector[DynamicVector[Float64]]](gram, "", True)

fn compute_style_loss(gram_target: DynamicVector[DynamicVector[Float64]], gram_generated: DynamicVector[DynamicVector[Float64]], n_channels: Int) -> OmniResult[Float64]:
    if len(gram_target) != n_channels or len(gram_generated) != n_channels:
        return OmniResult[Float64](0.0, "Gram matrix dimension mismatch.", False)

    var loss: Float64 = 0.0
    for i in range(n_channels):
        for j in range(n_channels):
            var diff = gram_target[i][j] - gram_generated[i][j]
            loss += diff * diff

    loss = loss / Float64(n_channels * n_channels)
    return OmniResult[Float64](loss, "", True)
