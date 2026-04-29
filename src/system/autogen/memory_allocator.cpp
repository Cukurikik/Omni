#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// OMNI AUTOGEN: Memory Allocator
// C++ custom memory arena for efficiently allocating and freeing large conversation
// context windows during multi-agent loop iterations without heap fragmentation.
// Source: microsoft/autogen

namespace omni::autogen {

class ContextArena {
private:
    char* pool;
    size_t total_size;
    size_t current_offset;

public:
    ContextArena(size_t size_bytes) {
        total_size = size_bytes;
        current_offset = 0;
        pool = (char*)malloc(total_size);
        if (!pool) {
            fprintf(stderr, "FATAL: Failed to allocate %zu bytes for ContextArena\n", size_bytes);
            exit(1);
        }
    }

    ~ContextArena() {
        if (pool) {
            free(pool);
        }
    }

    // Bump pointer allocation
    void* allocate(size_t size) {
        // Align to 8 bytes
        size_t aligned_size = (size + 7) & ~7;
        
        if (current_offset + aligned_size > total_size) {
            fprintf(stderr, "ContextArena OOM. Cannot allocate %zu bytes.\n", size);
            return nullptr;
        }

        void* ptr = pool + current_offset;
        current_offset += aligned_size;
        return ptr;
    }

    // Reset arena for the next conversation turn
    void reset() {
        current_offset = 0;
        // Optionally memset to 0 for security, skipping for performance
    }
    
    // Store a string in the arena
    char* store_string(const char* str) {
        size_t len = strlen(str) + 1;
        char* dest = (char*)allocate(len);
        if (dest) {
            memcpy(dest, str, len);
        }
        return dest;
    }
};

} // namespace omni::autogen
