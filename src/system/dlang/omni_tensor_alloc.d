// OMNI Framework - Fast Tensor Allocator in D
// High-performance GC-free allocation for inference nodes

module omni.system.tensor_alloc;

import core.stdc.stdlib : malloc, free;
import core.stdc.string : memset;

struct TensorPool {
    private void* buffer;
    private size_t capacity;
    private size_t offset;

    this(size_t size) @nogc nothrow {
        buffer = malloc(size);
        capacity = size;
        offset = 0;
        if (buffer) {
            memset(buffer, 0, capacity);
        }
    }

    ~this() @nogc nothrow {
        if (buffer) {
            free(buffer);
            buffer = null;
        }
    }

    void* allocate(size_t size, size_t alignment = 16) @nogc nothrow {
        if (!buffer) return null;

        size_t remainder = offset % alignment;
        size_t padding = (remainder == 0) ? 0 : (alignment - remainder);

        if (offset + padding + size > capacity) {
            return null; // Out of memory in this pool
        }

        offset += padding;
        void* ptr = buffer + offset;
        offset += size;

        return ptr;
    }

    void reset() @nogc nothrow {
        offset = 0;
    }
}
