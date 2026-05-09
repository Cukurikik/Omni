#include <stdlib.h>

void* allocate_chem_graph(size_t nodes, size_t edges) {
    size_t total_size = (nodes * sizeof(int)) + (edges * sizeof(int) * 2);
    void* ptr = malloc(total_size);
    return ptr;
}

void free_chem_graph(void* ptr) {
    if (ptr) {
        free(ptr);
    }
}
