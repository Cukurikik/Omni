#pragma once
#include <cstdint>
#include <cstddef>
#include <vector>

extern "C" {
    // Definisi C-Struct yang harus sama dengan OmniBuffer di Rust
    struct OmniBuffer {
        uint8_t* data;
        size_t length;
        size_t capacity;
    };

    // Fungsi dari Rust CDyLib yang akan dilink secara dinamis
    OmniBuffer* omni_allocate(size_t size);
    void omni_free(OmniBuffer* buffer);
    void omni_mutate_matrix(OmniBuffer* buffer);
}

namespace omni {
    /// Zero-Copy Tensor Wrapper.
    /// Kelas ini TIDAK MENG-COPY memori. Hanya melingkupi raw pointer
    /// yang didapat dari Rust OMNI-ABI.
    class TensorView {
    private:
        OmniBuffer* buffer;

    public:
        // Membuat TensorView baru yang memanggil allocator Rust di balik layar.
        TensorView(size_t size) {
            buffer = omni_allocate(size);
        }

        ~TensorView() {
            if (buffer) {
                omni_free(buffer);
                buffer = nullptr;
            }
        }

        // Pass pointer ke Rust untuk melakukan operasi (0 milidetik!)
        void mutate_in_rust() {
            omni_mutate_matrix(buffer);
        }

        // Akses langsung data C-Struct tanpa duplikasi
        uint8_t* data() const {
            return buffer->data;
        }

        size_t size() const {
            return buffer->length;
        }

        // Jangan izinkan copy constructor untuk mencegah segfault
        TensorView(const TensorView&) = delete;
        TensorView& operator=(const TensorView&) = delete;
    };
}
