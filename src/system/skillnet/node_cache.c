#include <stdlib.h>
#include <string.h>

typedef struct {
    void* cache_ptr;
    const char* error;
    int is_ok;
} OmniResultCache;

OmniResultCache allocate_skill_node_cache(int num_nodes) {
    if (num_nodes <= 0) return (OmniResultCache){NULL, "Node count <= 0", 0};
    
    // Allocate 256 bytes per skill node state
    size_t alloc_size = num_nodes * 256;
    void* ptr = malloc(alloc_size);
    if (!ptr) return (OmniResultCache){NULL, "OOM during cache allocation", 0};
    
    memset(ptr, 0, alloc_size);
    return (OmniResultCache){ptr, NULL, 1};
}
