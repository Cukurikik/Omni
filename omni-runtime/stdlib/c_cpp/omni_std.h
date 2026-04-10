#ifndef OMNI_STD_H
#define OMNI_STD_H

// ============================================================
// OMNI C/C++ Bridge — System Layer Header
// ============================================================
// Layer: System (Bare-metal I/O, FFI, Kernel Interface)
// Header tunggal untuk C dan C++ — TIDAK perlu build system.
// Cukup #include "omni_std.h" dan link ke omni_core.
// ============================================================

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef _WIN32
  #ifdef OMNI_EXPORT
    #define OMNI_API __declspec(dllexport)
  #else
    #define OMNI_API __declspec(dllimport)
  #endif
#else
  #define OMNI_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

// ─── OMNI C-ABI Core Functions ─────────────────────────────

/** Eksekutor utama OMNI engine */
OMNI_API void* __omni_ffi(void* args_buffer, size_t len);

/** Alokasi OmniBuffer di Rust heap */
OMNI_API void* __omni_buffer_alloc(size_t size);

/** Dealokasi OmniBuffer */
OMNI_API void __omni_buffer_free(void* ptr, size_t len);

// ─── OMNI Result Struct ────────────────────────────────────

typedef struct {
    void*    data;
    size_t   len;
    uint8_t  status;   // 0x00 = OK, 0x01+ = error code
    char     error_msg[256];
} OmniResult;

/** Eksekusi dengan Result struct penuh */
OMNI_API OmniResult __omni_ffi_result(void* args_buffer, size_t len);

#ifdef __cplusplus
} // extern "C"

// ─── C++ RAII Wrapper ──────────────────────────────────────
#include <memory>
#include <stdexcept>
#include <string>

namespace omni {

    /// RAII smart pointer untuk OmniBuffer
    struct BufferDeleter {
        size_t len;
        void operator()(void* ptr) const {
            if (ptr) __omni_buffer_free(ptr, len);
        }
    };

    using OmniBufferPtr = std::unique_ptr<void, BufferDeleter>;

    /// Zero-cost inline wrapper
    template <typename T>
    inline OmniResult execute(const T& data) {
        return __omni_ffi_result(
            const_cast<void*>(static_cast<const void*>(&data)),
            sizeof(T)
        );
    }

    /// Execute dengan byte vector
    inline OmniResult execute(const void* data, size_t len) {
        return __omni_ffi_result(const_cast<void*>(data), len);
    }

    /// Allocate managed buffer
    inline OmniBufferPtr alloc_buffer(size_t size) {
        void* ptr = __omni_buffer_alloc(size);
        if (!ptr) throw std::runtime_error("[OMNI-E901] Buffer allocation failed");
        return OmniBufferPtr(ptr, BufferDeleter{size});
    }

} // namespace omni
#endif // __cplusplus

#endif // OMNI_STD_H
