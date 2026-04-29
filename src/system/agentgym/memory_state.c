#include <stdlib.h>
#include <string.h>

typedef struct {
    void* state_ptr;
    const char* error;
    int is_ok;
} OmniResultPtr;

OmniResultPtr allocate_agent_state(size_t state_size) {
    if (state_size == 0) return (OmniResultPtr){NULL, "State size is 0", 0};
    
    void* ptr = malloc(state_size);
    if (!ptr) return (OmniResultPtr){NULL, "OOM during state allocation", 0};
    
    memset(ptr, 0, state_size);
    return (OmniResultPtr){ptr, NULL, 1};
}
