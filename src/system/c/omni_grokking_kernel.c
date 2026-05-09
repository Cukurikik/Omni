// OMNI High-Performance Grokking Dataset Generation Kernel
// Implements fast modular arithmetic for algorithmic datasets
#include <stdint.h>
#include <stdlib.h>

typedef struct {
    uint32_t operand_a;
    uint32_t operand_b;
    uint32_t result;
} ModuloOperation;

void generate_mod_addition_dataset(ModuloOperation* dataset, size_t size, uint32_t p) {
    for (size_t i = 0; i < size; ++i) {
        // Fast deterministic pseudo-random generation for algorithmic dataset
        uint32_t a = (uint32_t)(rand() % p);
        uint32_t b = (uint32_t)(rand() % p);
        
        dataset[i].operand_a = a;
        dataset[i].operand_b = b;
        dataset[i].result = (a + b) % p;
    }
}
