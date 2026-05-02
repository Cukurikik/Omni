/* @omni-domain System Layer (Style Tensor Allocation)
   @omni-source various/stylellm
   @omni-description Style Tensor Alloc mimicking arena allocator for style tensors in C.
   @omni-requirement zero-mock, monadic-error */
#include <stdlib.h>
#include <string.h>
typedef struct { void* data; char* error; int is_ok; } OmniResult;
typedef struct { float* arena; int capacity; int offset; } StyleArena;

OmniResult style_arena_init(StyleArena* a, int capacity) {
    OmniResult r;
    if (capacity <= 0) { r.data=NULL; r.error="Capacity must be > 0."; r.is_ok=0; return r; }
    a->arena = (float*)calloc(capacity, sizeof(float));
    if (!a->arena) { r.data=NULL; r.error="Alloc failed."; r.is_ok=0; return r; }
    a->capacity = capacity; a->offset = 0;
    r.data=a; r.error=NULL; r.is_ok=1; return r;
}

OmniResult style_arena_alloc(StyleArena* a, int count) {
    OmniResult r;
    if (!a || a->offset + count > a->capacity) { r.data=NULL; r.error="Arena overflow."; r.is_ok=0; return r; }
    float* ptr = a->arena + a->offset;
    a->offset += count;
    r.data=ptr; r.error=NULL; r.is_ok=1; return r;
}

void style_arena_reset(StyleArena* a) { if (a) a->offset = 0; }
void style_arena_free(StyleArena* a) { if (a && a->arena) { free(a->arena); a->arena = NULL; } }
