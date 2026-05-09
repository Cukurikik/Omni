// OMNI System — Odin Context Manager
// Provides ultra-low-latency implicit context passing for kernel threads

package omni_system

import "core:fmt"
import "core:mem"

// Custom implicit context for OMNI worker threads
OmniThreadContext :: struct {
    worker_id: u32,
    arena: mem.Arena,
    num_tensors_processed: u64,
}

// Thread-local storage for context
@(thread_local)
current_thread_ctx: OmniThreadContext

init_thread_context :: proc(id: u32, buffer: []u8) {
    current_thread_ctx.worker_id = id
    mem.arena_init(&current_thread_ctx.arena, buffer)
    current_thread_ctx.num_tensors_processed = 0
    fmt.printf("OMNI Odin Kernel: Initialized Thread %d\n", id)
}

process_tensor_batch :: proc(batch_size: u64) {
    // Implicitly uses current_thread_ctx
    current_thread_ctx.num_tensors_processed += batch_size
    fmt.printf("Thread %d processed %d tensors (Total: %d)\n", 
        current_thread_ctx.worker_id, 
        batch_size, 
        current_thread_ctx.num_tensors_processed)
}
