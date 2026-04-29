#include <cstdint>

extern "C" {
    // AutoML architecture checksum generator
    uint32_t automl_hash_architecture(const uint32_t* layer_dims, uint32_t num_layers) {
        uint32_t hash = 0x811c9dc5; // FNV-1a offset basis
        for (uint32_t i = 0; i < num_layers; ++i) {
            uint32_t val = layer_dims[i];
            hash ^= (val & 0xFF);
            hash *= 0x01000193; // FNV prime
            hash ^= ((val >> 8) & 0xFF);
            hash *= 0x01000193;
            hash ^= ((val >> 16) & 0xFF);
            hash *= 0x01000193;
            hash ^= ((val >> 24) & 0xFF);
            hash *= 0x01000193;
        }
        return hash;
    }
}
