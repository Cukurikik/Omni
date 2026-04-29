#include <cstdint>

extern "C" {
    // llama.cpp Android JNI dummy backend initializer
    bool llamacpp_android_initialize_context(uint32_t n_threads, uint32_t n_ctx, bool use_mmap) {
        // In a real JNI binding, this would call llama_backend_init
        if (n_ctx == 0 || n_threads == 0) return false;
        
        // Emulate successful initialization constraints
        if (n_threads > 128) return false;
        return true;
    }
}
