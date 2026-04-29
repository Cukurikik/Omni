// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Redis Cache (OMNI Zero-Mock Implementation)
// Implements deterministic Least Recently Used (LRU) mathematical pointer update abstraction.

#include <stdlib.h>
#include <string.h>

// Omni standard error wrapping in pure C
typedef struct {
    int* value;       // Array of cache keys in LRU order (most recent first)
    int length;
    int is_ok;
    char error[256];
} LRUResult;

LRUResult omni_redis_lru_access(int* current_state, int length, int accessed_element, int capacity) {
    LRUResult res;
    res.value = NULL;
    res.length = 0;
    
    if (capacity <= 0 || length < 0 || length > capacity) {
        res.is_ok = 0;
        strcpy(res.error, "Invalid capacity boundaries.");
        return res;
    }
    
    int* new_state = (int*)malloc(sizeof(int) * capacity);
    
    // Check if element exists
    int found_idx = -1;
    for (int i = 0; i < length; i++) {
        if (current_state[i] == accessed_element) {
            found_idx = i;
            break;
        }
    }
    
    new_state[0] = accessed_element; // Move to front
    int ptr = 1;
    
    if (found_idx != -1) {
        // Element found, shift everything before it right natively
        for (int i = 0; i < found_idx; i++) {
            if (ptr < capacity) new_state[ptr++] = current_state[i];
        }
        for (int i = found_idx + 1; i < length; i++) {
             if (ptr < capacity) new_state[ptr++] = current_state[i];
        }
    } else {
        // Element not found, add to front, discard last if over capacity
        for (int i = 0; i < length; i++) {
            if (ptr < capacity) new_state[ptr++] = current_state[i];
        }
    }
    
    res.is_ok = 1;
    res.value = new_state;
    res.length = ptr;
    return res;
}
