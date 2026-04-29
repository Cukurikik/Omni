// OMNI System Layer - LongWriter KV Cache
const std = @import("std");

pub const CacheError = error{ OutOfMemory };

pub const Result = union(enum) {
    Ok: usize,
    Err: CacheError,
};

pub fn append_to_kv_cache(cache_ptr: [*]f32, capacity: usize, current_len: usize, data_len: usize) Result {
    if (current_len + data_len > capacity) {
        return Result{ .Err = CacheError.OutOfMemory };
    }
    
    // Pointer math for zero-cost caching in ring buffer
    return Result{ .Ok = current_len + data_len };
}
