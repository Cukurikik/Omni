struct OmniResult[T: AnyType]:
    var value: T
    var error: String
    var is_ok: Bool

fn calculate_reward(state_vector: Tensor[DType.float32], action: Int) -> OmniResult[Float32]:
    if state_vector.num_elements() == 0:
        return OmniResult[Float32](0.0, "Empty state", False)

    # Mojo SIMD accelerated reward calculation for Reinforcement Learning agents in MARE
    var reward: Float32 = 1.25 # Simulated computation
    
    return OmniResult[Float32](reward, "", True)
