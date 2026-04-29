import omni
from omni.system import zero_copy

def allocate_kv_cache(num_blocks: int, block_size: int) -> omni.Result:
    '''Zero-copy KV cache allocation for vLLM in OMNI.'''
    try:
        buffer = zero_copy.allocate(num_blocks * block_size)
        return omni.Result.Ok(buffer)
    except Exception as e:
        return omni.Result.Err(e)
