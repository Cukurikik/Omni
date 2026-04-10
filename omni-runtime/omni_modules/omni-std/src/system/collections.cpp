// ============================================================
// ⚡ omni-std/system/collections.cpp — C++ Collection Primitives 
// ============================================================

#include <vector>
#include <unordered_map>
#include <string>
#include <cstdint>
#include <cstring>

extern "C" {

// C++ vector wrapper for OMNI engine array pointers
struct OmniArrayBase {
    void* data;
    size_t length;
    size_t capacity;
    size_t element_size;
};

// ─── OMNI Vec Primitive ──────────────────────────────────
// Provides fast vector operations backing `Vec<T>` in OMNI.

void* omni_vec_create(size_t element_size) {
    auto vec = new OmniArrayBase();
    vec->data = nullptr;
    vec->length = 0;
    vec->capacity = 0;
    vec->element_size = element_size;
    return vec;
}

void omni_vec_push(void* vec_ptr, const void* element_data) {
    if (!vec_ptr || !element_data) return;
    auto vec = static_cast<OmniArrayBase*>(vec_ptr);
    
    if (vec->length >= vec->capacity) {
        size_t new_cap = vec->capacity == 0 ? 8 : vec->capacity * 2;
        void* new_data = malloc(new_cap * vec->element_size);
        if (vec->data) {
            std::memcpy(new_data, vec->data, vec->length * vec->element_size);
            free(vec->data);
        }
        vec->data = new_data;
        vec->capacity = new_cap;
    }
    
    // Copy the struct/primitive over
    uint8_t* dest = static_cast<uint8_t*>(vec->data) + (vec->length * vec->element_size);
    std::memcpy(dest, element_data, vec->element_size);
    vec->length++;
}

void omni_vec_free(void* vec_ptr) {
    if (!vec_ptr) return;
    auto vec = static_cast<OmniArrayBase*>(vec_ptr);
    if (vec->data) {
        free(vec->data);
    }
    delete vec;
}

}
