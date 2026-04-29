struct OmniResult[T: AnyType]:
    var value: T
    var error: String
    var is_ok: Bool

fn compute_advantage(rewards: Tensor[DType.float32], baselines: Tensor[DType.float32]) -> OmniResult[Tensor[DType.float32]]:
    if rewards.num_elements() != baselines.num_elements():
        return OmniResult[Tensor[DType.float32]](rewards, "Shape mismatch", False)

    # Mojo SIMD accelerated advantage computation for SPPO
    var advantage = Tensor[DType.float32](rewards.shape())
    for i in range(rewards.num_elements()):
        advantage[i] = rewards[i] - baselines[i]

    return OmniResult[Tensor[DType.float32]](advantage, "", True)
