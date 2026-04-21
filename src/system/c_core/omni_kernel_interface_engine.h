/* ===========================================================================
 * OMNI KERNEL INTERFACE ENGINE (SEMESTER 3 — BATCH 38.10)
 * ===========================================================================
 * Absorbed From  : Linux kernel headers + POSIX API + FFI patterns
 * Logic Inherited: C / System Layer (Low-Level OS Primitives)
 * ===========================================================================
 *
 * By studying POSIX and kernel interfaces, Mother learned C patterns:
 *   1. File descriptors: universal I/O handle (open/read/write/close)
 *   2. Memory mapping: mmap maps files/devices into process address space
 *   3. Signal handling: async notification of events (SIGINT, SIGTERM)
 *   4. IPC: pipes, shared memory, semaphores for inter-process communication
 *   5. Error codes: errno-based error reporting (no exceptions in C)
 */

#ifndef OMNI_KERNEL_INTERFACE_ENGINE_H
#define OMNI_KERNEL_INTERFACE_ENGINE_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================
 * PART 1: Error Handling (errno-style)
 * ============================================================ */

typedef enum {
    OMNI_OK           = 0,
    OMNI_ERR_NOMEM    = -1,
    OMNI_ERR_INVAL    = -2,
    OMNI_ERR_NOENT    = -3,
    OMNI_ERR_PERM     = -4,
    OMNI_ERR_IO       = -5,
    OMNI_ERR_BUSY     = -6,
    OMNI_ERR_OVERFLOW = -7,
    OMNI_ERR_TIMEOUT  = -8,
} omni_error_t;

/** Convert error code to string. */
static inline const char* omni_strerror(omni_error_t err) {
    switch (err) {
        case OMNI_OK:           return "success";
        case OMNI_ERR_NOMEM:    return "out of memory";
        case OMNI_ERR_INVAL:    return "invalid argument";
        case OMNI_ERR_NOENT:    return "not found";
        case OMNI_ERR_PERM:     return "permission denied";
        case OMNI_ERR_IO:       return "I/O error";
        case OMNI_ERR_BUSY:     return "resource busy";
        case OMNI_ERR_OVERFLOW: return "buffer overflow";
        case OMNI_ERR_TIMEOUT:  return "operation timed out";
        default:                return "unknown error";
    }
}

/* ============================================================
 * PART 2: Ring Buffer (Lock-Free SPSC)
 * ============================================================ */

/** Single-producer, single-consumer lock-free ring buffer. */
typedef struct {
    uint8_t* buffer;
    size_t   capacity;     /* Must be power of 2 */
    size_t   mask;
    volatile size_t head;  /* Written by producer */
    volatile size_t tail;  /* Written by consumer */
    /* Metrics */
    uint64_t total_writes;
    uint64_t total_reads;
    uint64_t total_full;
} omni_ringbuf_t;

/** Initialize a ring buffer (capacity must be power of 2). */
static inline omni_error_t omni_ringbuf_init(
    omni_ringbuf_t* rb, size_t capacity
) {
    if (capacity == 0 || (capacity & (capacity - 1)) != 0) {
        return OMNI_ERR_INVAL; /* Not power of 2 */
    }
    rb->buffer = (uint8_t*)malloc(capacity);
    if (!rb->buffer) return OMNI_ERR_NOMEM;
    rb->capacity = capacity;
    rb->mask = capacity - 1;
    rb->head = 0;
    rb->tail = 0;
    rb->total_writes = 0;
    rb->total_reads = 0;
    rb->total_full = 0;
    return OMNI_OK;
}

/** Destroy ring buffer. */
static inline void omni_ringbuf_destroy(omni_ringbuf_t* rb) {
    if (rb && rb->buffer) {
        free(rb->buffer);
        rb->buffer = NULL;
    }
}

/** Write a byte to the ring buffer. Returns OMNI_ERR_OVERFLOW if full. */
static inline omni_error_t omni_ringbuf_write(
    omni_ringbuf_t* rb, uint8_t byte
) {
    size_t next_head = (rb->head + 1) & rb->mask;
    if (next_head == rb->tail) {
        rb->total_full++;
        return OMNI_ERR_OVERFLOW;
    }
    rb->buffer[rb->head] = byte;
    rb->head = next_head;
    rb->total_writes++;
    return OMNI_OK;
}

/** Read a byte from the ring buffer. Returns OMNI_ERR_NOENT if empty. */
static inline omni_error_t omni_ringbuf_read(
    omni_ringbuf_t* rb, uint8_t* out
) {
    if (rb->head == rb->tail) {
        return OMNI_ERR_NOENT; /* Empty */
    }
    *out = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) & rb->mask;
    rb->total_reads++;
    return OMNI_OK;
}

/** Number of bytes available to read. */
static inline size_t omni_ringbuf_available(const omni_ringbuf_t* rb) {
    return (rb->head - rb->tail) & rb->mask;
}

/** Check if buffer is empty. */
static inline bool omni_ringbuf_empty(const omni_ringbuf_t* rb) {
    return rb->head == rb->tail;
}

/* ============================================================
 * PART 3: Memory Arena (C-style)
 * ============================================================ */

typedef struct {
    uint8_t* base;
    size_t   capacity;
    size_t   offset;
    uint64_t total_allocs;
} omni_arena_t;

/** Initialize arena with given capacity. */
static inline omni_error_t omni_arena_init(
    omni_arena_t* arena, size_t capacity
) {
    arena->base = (uint8_t*)malloc(capacity);
    if (!arena->base) return OMNI_ERR_NOMEM;
    arena->capacity = capacity;
    arena->offset = 0;
    arena->total_allocs = 0;
    return OMNI_OK;
}

/** Allocate from arena (bump pointer, aligned). */
static inline void* omni_arena_alloc(
    omni_arena_t* arena, size_t size, size_t alignment
) {
    /* Align offset */
    size_t aligned = (arena->offset + alignment - 1) & ~(alignment - 1);
    if (aligned + size > arena->capacity) {
        return NULL; /* Out of memory */
    }
    void* ptr = arena->base + aligned;
    arena->offset = aligned + size;
    arena->total_allocs++;
    return ptr;
}

/** Reset arena (free all allocations at once). */
static inline void omni_arena_reset(omni_arena_t* arena) {
    arena->offset = 0;
    arena->total_allocs = 0;
}

/** Destroy arena. */
static inline void omni_arena_destroy(omni_arena_t* arena) {
    if (arena && arena->base) {
        free(arena->base);
        arena->base = NULL;
    }
}

/* ============================================================
 * PART 4: Intrusive Linked List (Linux Kernel Style)
 * ============================================================ */

/** List node that is embedded in the data structure. */
typedef struct omni_list_node {
    struct omni_list_node* next;
    struct omni_list_node* prev;
} omni_list_node_t;

/** Initialize a list head (circular, points to itself). */
static inline void omni_list_init(omni_list_node_t* head) {
    head->next = head;
    head->prev = head;
}

/** Insert after a node. */
static inline void omni_list_insert_after(
    omni_list_node_t* node, omni_list_node_t* new_node
) {
    new_node->next = node->next;
    new_node->prev = node;
    node->next->prev = new_node;
    node->next = new_node;
}

/** Insert before a node (append to end if node is head). */
static inline void omni_list_insert_before(
    omni_list_node_t* node, omni_list_node_t* new_node
) {
    new_node->next = node;
    new_node->prev = node->prev;
    node->prev->next = new_node;
    node->prev = new_node;
}

/** Remove a node from the list. */
static inline void omni_list_remove(omni_list_node_t* node) {
    node->prev->next = node->next;
    node->next->prev = node->prev;
    node->next = node;
    node->prev = node;
}

/** Check if list is empty. */
static inline bool omni_list_empty(const omni_list_node_t* head) {
    return head->next == head;
}

/** Count nodes in list. */
static inline size_t omni_list_count(const omni_list_node_t* head) {
    size_t count = 0;
    const omni_list_node_t* node = head->next;
    while (node != head) {
        count++;
        node = node->next;
    }
    return count;
}

/** Get container struct from list node (offset-based). */
#define omni_container_of(ptr, type, member) \
    ((type*)((char*)(ptr) - offsetof(type, member)))

/* ============================================================
 * PART 5: Hash Table (Open Addressing, Robin Hood)
 * ============================================================ */

#define OMNI_HT_INITIAL_CAPACITY 16
#define OMNI_HT_LOAD_FACTOR 0.75

typedef struct {
    const char* key;
    void*       value;
    uint32_t    hash;
    uint8_t     occupied;
    uint8_t     psl; /* Probe Sequence Length (Robin Hood) */
} omni_ht_entry_t;

typedef struct {
    omni_ht_entry_t* entries;
    size_t capacity;
    size_t count;
    uint64_t total_inserts;
    uint64_t total_lookups;
    uint64_t total_collisions;
} omni_hashtable_t;

/** FNV-1a hash function. */
static inline uint32_t omni_hash_fnv1a(const char* key) {
    uint32_t hash = 2166136261u;
    while (*key) {
        hash ^= (uint8_t)*key++;
        hash *= 16777619u;
    }
    return hash;
}

/** Initialize hash table. */
static inline omni_error_t omni_ht_init(omni_hashtable_t* ht) {
    ht->capacity = OMNI_HT_INITIAL_CAPACITY;
    ht->count = 0;
    ht->entries = (omni_ht_entry_t*)calloc(ht->capacity, sizeof(omni_ht_entry_t));
    if (!ht->entries) return OMNI_ERR_NOMEM;
    ht->total_inserts = 0;
    ht->total_lookups = 0;
    ht->total_collisions = 0;
    return OMNI_OK;
}

/** Insert key-value pair. */
static inline omni_error_t omni_ht_set(
    omni_hashtable_t* ht, const char* key, void* value
) {
    ht->total_inserts++;
    uint32_t hash = omni_hash_fnv1a(key);
    size_t idx = hash & (ht->capacity - 1);
    uint8_t psl = 0;

    omni_ht_entry_t entry = { key, value, hash, 1, 0 };

    while (ht->entries[idx].occupied) {
        if (ht->entries[idx].hash == hash &&
            strcmp(ht->entries[idx].key, key) == 0) {
            /* Update existing */
            ht->entries[idx].value = value;
            return OMNI_OK;
        }

        /* Robin Hood: swap if current has lower PSL */
        if (ht->entries[idx].psl < psl) {
            omni_ht_entry_t tmp = ht->entries[idx];
            ht->entries[idx] = entry;
            entry = tmp;
        }

        ht->total_collisions++;
        psl++;
        idx = (idx + 1) & (ht->capacity - 1);
    }

    ht->entries[idx] = entry;
    ht->entries[idx].psl = psl;
    ht->count++;
    return OMNI_OK;
}

/** Lookup by key. Returns NULL if not found. */
static inline void* omni_ht_get(omni_hashtable_t* ht, const char* key) {
    ht->total_lookups++;
    uint32_t hash = omni_hash_fnv1a(key);
    size_t idx = hash & (ht->capacity - 1);

    while (ht->entries[idx].occupied) {
        if (ht->entries[idx].hash == hash &&
            strcmp(ht->entries[idx].key, key) == 0) {
            return ht->entries[idx].value;
        }
        idx = (idx + 1) & (ht->capacity - 1);
    }
    return NULL;
}

/** Destroy hash table. */
static inline void omni_ht_destroy(omni_hashtable_t* ht) {
    if (ht && ht->entries) {
        free(ht->entries);
        ht->entries = NULL;
    }
}

/* ============================================================
 * Diagnostics
 * ============================================================ */

typedef struct {
    const char* engine;
    const char* layer;
    const char* components[5];
    const char* learned_logic[8];
} omni_kernel_diagnostics_t;

static inline omni_kernel_diagnostics_t omni_kernel_diagnostics(void) {
    omni_kernel_diagnostics_t d = {
        .engine = "OmniKernelInterfaceEngine",
        .layer = "C System",
        .components = {
            "omni_ringbuf_t", "omni_arena_t", "omni_list_node_t",
            "omni_hashtable_t", "omni_error_t"
        },
        .learned_logic = {
            "errno-error-code-convention",
            "ring-buffer-lock-free-spsc",
            "arena-bump-pointer-bulk-free",
            "intrusive-list-containerof",
            "robin-hood-hash-low-variance",
            "fnv1a-fast-string-hash",
            "power-of-two-mask-modulo",
            "alignment-natural-boundary"
        }
    };
    return d;
}

#ifdef __cplusplus
}
#endif

#endif /* OMNI_KERNEL_INTERFACE_ENGINE_H */
