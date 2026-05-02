# @omni-domain Compute Layer (DeepSpeed ZeRO)
# @omni-source microsoft/DeepSpeed
# @omni-description DeepSpeed ZeRO Optimizer mimicking memory partitioning in Mojo.
# @omni-requirement zero-mock, monadic-error

struct OmniResult[T: AnyType]:
    var data: T
    var error: String
    var is_ok: Bool

fn compute_partition_size(total_params: Int, num_gpus: Int) -> OmniResult[Int]:
    if num_gpus <= 0:
        return OmniResult[Int](0, "Number of GPUs must be > 0.", False)
    if total_params <= 0:
        return OmniResult[Int](0, "Total params must be > 0.", False)
    var partition = total_params // num_gpus
    var remainder = total_params % num_gpus
    return OmniResult[Int](partition + (1 if remainder > 0 else 0), "", True)

fn estimate_zero_stage_memory(total_params: Int, num_gpus: Int, stage: Int, dtype_bytes: Int = 2) -> OmniResult[Int]:
    if stage < 1 or stage > 3:
        return OmniResult[Int](0, "ZeRO stage must be 1, 2, or 3.", False)
    if num_gpus <= 0 or total_params <= 0:
        return OmniResult[Int](0, "Invalid params.", False)

    var params_per_gpu = total_params // num_gpus
    var model_mem = total_params * dtype_bytes
    var optimizer_mem = total_params * 8  # Adam: 2 states * 4 bytes each
    var gradient_mem = total_params * dtype_bytes

    var per_gpu_mem: Int = 0

    if stage == 1:
        # Stage 1: Partition optimizer states only
        per_gpu_mem = model_mem + gradient_mem + (optimizer_mem // num_gpus)
    elif stage == 2:
        # Stage 2: Partition optimizer + gradients
        per_gpu_mem = model_mem + (gradient_mem // num_gpus) + (optimizer_mem // num_gpus)
    else:
        # Stage 3: Partition everything
        per_gpu_mem = (model_mem // num_gpus) + (gradient_mem // num_gpus) + (optimizer_mem // num_gpus)

    return OmniResult[Int](per_gpu_mem, "", True)

fn compute_communication_volume(total_params: Int, num_gpus: Int, stage: Int) -> OmniResult[Int]:
    if stage < 1 or stage > 3:
        return OmniResult[Int](0, "ZeRO stage must be 1, 2, or 3.", False)

    var volume: Int = 0
    if stage == 1:
        volume = 2 * total_params  # all-reduce gradients
    elif stage == 2:
        volume = 2 * total_params  # reduce-scatter + all-gather
    else:
        volume = 3 * total_params  # all-gather params + reduce-scatter grads + all-gather updates

    return OmniResult[Int](volume * 2, "", True)  # 2 bytes per param (fp16)
