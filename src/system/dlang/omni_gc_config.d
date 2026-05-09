// OMNI Framework Garbage Collection Tuning in D
import core.memory;

extern(C) void omni_init_d_runtime() {
    // Disable GC for deterministic latency in compute paths
    GC.disable();
    
    // Reserve specific memory block
    GC.reserve(1024 * 1024 * 64); // 64 MB
}

extern(C) void omni_force_gc_collection() {
    // Only run when explicitly called by OMNI memory manager
    GC.enable();
    GC.collect();
    GC.disable();
}
