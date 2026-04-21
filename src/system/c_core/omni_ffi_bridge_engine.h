/* ===========================================================================
 * OMNI FFI BRIDGE ENGINE (SEMESTER 3 — BATCH 38.10)
 * ===========================================================================
 * Absorbed From  : FFI patterns + libffi + C ABI + calling conventions
 * Logic Inherited: C / System Layer (Foreign Function Interface Bridge)
 * ===========================================================================
 *
 * By studying FFI and C ABI, Mother learned:
 *   1. C ABI is the universal bridge between languages
 *   2. Opaque handles (void*) hide implementation from callers
 *   3. Callback function pointers enable language-agnostic hooks
 *   4. Versioned struct patterns ensure ABI compatibility
 *   5. Thread-local storage provides per-thread context
 */

#ifndef OMNI_FFI_BRIDGE_ENGINE_H
#define OMNI_FFI_BRIDGE_ENGINE_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================
 * PART 1: Opaque Handle System
 * ============================================================ */

/** Opaque handle type (hides implementation from callers). */
typedef struct omni_handle_s* omni_handle_t;

/** Handle metadata for type safety. */
typedef struct {
    uint32_t magic;         /* Magic number for validation */
    uint32_t type_id;       /* Type discriminator */
    uint32_t version;       /* API version */
    void*    inner;         /* Actual data pointer */
    void   (*destructor)(void*);  /* Custom cleanup function */
} omni_handle_data_t;

#define OMNI_HANDLE_MAGIC 0x4F4D4E49  /* "OMNI" */

/** Create a new handle wrapping an inner pointer. */
static inline omni_handle_t omni_handle_create(
    uint32_t type_id,
    void*    inner,
    void   (*destructor)(void*)
) {
    omni_handle_data_t* h = (omni_handle_data_t*)malloc(sizeof(omni_handle_data_t));
    if (!h) return NULL;
    h->magic = OMNI_HANDLE_MAGIC;
    h->type_id = type_id;
    h->version = 1;
    h->inner = inner;
    h->destructor = destructor;
    return (omni_handle_t)h;
}

/** Validate and unwrap a handle. Returns NULL on invalid handle. */
static inline void* omni_handle_unwrap(omni_handle_t handle, uint32_t expected_type) {
    omni_handle_data_t* h = (omni_handle_data_t*)handle;
    if (!h || h->magic != OMNI_HANDLE_MAGIC || h->type_id != expected_type) {
        return NULL;
    }
    return h->inner;
}

/** Destroy a handle and call its destructor. */
static inline void omni_handle_destroy(omni_handle_t handle) {
    omni_handle_data_t* h = (omni_handle_data_t*)handle;
    if (!h || h->magic != OMNI_HANDLE_MAGIC) return;
    if (h->destructor && h->inner) {
        h->destructor(h->inner);
    }
    h->magic = 0; /* Invalidate */
    free(h);
}

/* ============================================================
 * PART 2: Callback Registry
 * ============================================================ */

/** Generic callback function pointer type. */
typedef void (*omni_callback_fn)(void* context, const void* data, size_t data_len);

/** Callback entry. */
typedef struct {
    const char*       name;
    omni_callback_fn  fn;
    void*             context;
    uint64_t          call_count;
    bool              active;
} omni_callback_entry_t;

#define OMNI_MAX_CALLBACKS 64

/** Callback registry for managing event hooks. */
typedef struct {
    omni_callback_entry_t entries[OMNI_MAX_CALLBACKS];
    size_t count;
    uint64_t total_dispatches;
} omni_callback_registry_t;

/** Initialize callback registry. */
static inline void omni_cb_init(omni_callback_registry_t* reg) {
    memset(reg, 0, sizeof(omni_callback_registry_t));
}

/** Register a callback. Returns index or -1 on failure. */
static inline int omni_cb_register(
    omni_callback_registry_t* reg,
    const char*       name,
    omni_callback_fn  fn,
    void*             context
) {
    if (reg->count >= OMNI_MAX_CALLBACKS) return -1;
    size_t idx = reg->count++;
    reg->entries[idx].name = name;
    reg->entries[idx].fn = fn;
    reg->entries[idx].context = context;
    reg->entries[idx].call_count = 0;
    reg->entries[idx].active = true;
    return (int)idx;
}

/** Dispatch callback by name. */
static inline void omni_cb_dispatch(
    omni_callback_registry_t* reg,
    const char*  name,
    const void*  data,
    size_t       data_len
) {
    reg->total_dispatches++;
    for (size_t i = 0; i < reg->count; i++) {
        if (reg->entries[i].active &&
            strcmp(reg->entries[i].name, name) == 0) {
            reg->entries[i].fn(reg->entries[i].context, data, data_len);
            reg->entries[i].call_count++;
        }
    }
}

/** Deactivate a callback by index. */
static inline void omni_cb_deactivate(omni_callback_registry_t* reg, int idx) {
    if (idx >= 0 && (size_t)idx < reg->count) {
        reg->entries[idx].active = false;
    }
}

/* ============================================================
 * PART 3: Versioned Struct (ABI Compatibility)
 * ============================================================ */

/** Versioned struct header — first field of any public struct. */
typedef struct {
    uint32_t struct_size;   /* sizeof(the_struct) — enables size-based version check */
    uint32_t version;       /* API version number */
    uint32_t flags;         /* Optional feature flags */
} omni_version_header_t;

/** Macro to initialize version header. */
#define OMNI_VERSION_HEADER(type, ver) \
    { .struct_size = sizeof(type), .version = (ver), .flags = 0 }

/** Check if a struct has a field (based on its size vs offset). */
#define OMNI_HAS_FIELD(header, type, field) \
    ((header)->struct_size >= offsetof(type, field) + sizeof(((type*)0)->field))

/* ============================================================
 * PART 4: String View (Non-Owning Slice)
 * ============================================================ */

/** Non-owning view into a string (pointer + length). */
typedef struct {
    const char* data;
    size_t      len;
} omni_strview_t;

/** Create string view from C string. */
static inline omni_strview_t omni_strview(const char* str) {
    return (omni_strview_t){ .data = str, .len = str ? strlen(str) : 0 };
}

/** Create string view from pointer and length. */
static inline omni_strview_t omni_strview_n(const char* str, size_t len) {
    return (omni_strview_t){ .data = str, .len = len };
}

/** Check equality. */
static inline bool omni_strview_eq(omni_strview_t a, omni_strview_t b) {
    if (a.len != b.len) return false;
    return memcmp(a.data, b.data, a.len) == 0;
}

/** Check if starts with prefix. */
static inline bool omni_strview_starts_with(omni_strview_t sv, const char* prefix) {
    size_t plen = strlen(prefix);
    if (sv.len < plen) return false;
    return memcmp(sv.data, prefix, plen) == 0;
}

/** Slice a string view. */
static inline omni_strview_t omni_strview_slice(
    omni_strview_t sv, size_t start, size_t end
) {
    if (start > sv.len) start = sv.len;
    if (end > sv.len) end = sv.len;
    if (start > end) start = end;
    return (omni_strview_t){ .data = sv.data + start, .len = end - start };
}

/* ============================================================
 * PART 5: Byte Buffer (Growable)
 * ============================================================ */

typedef struct {
    uint8_t* data;
    size_t   len;
    size_t   capacity;
} omni_bytebuf_t;

static inline int omni_bytebuf_init(omni_bytebuf_t* buf, size_t initial_cap) {
    buf->data = (uint8_t*)malloc(initial_cap);
    if (!buf->data) return -1;
    buf->len = 0;
    buf->capacity = initial_cap;
    return 0;
}

static inline int omni_bytebuf_append(
    omni_bytebuf_t* buf, const uint8_t* data, size_t len
) {
    if (buf->len + len > buf->capacity) {
        size_t new_cap = buf->capacity * 2;
        while (new_cap < buf->len + len) new_cap *= 2;
        uint8_t* new_data = (uint8_t*)realloc(buf->data, new_cap);
        if (!new_data) return -1;
        buf->data = new_data;
        buf->capacity = new_cap;
    }
    memcpy(buf->data + buf->len, data, len);
    buf->len += len;
    return 0;
}

static inline void omni_bytebuf_destroy(omni_bytebuf_t* buf) {
    if (buf && buf->data) { free(buf->data); buf->data = NULL; }
}

/* ============================================================
 * Diagnostics
 * ============================================================ */

typedef struct {
    const char* engine;
    const char* layer;
    const char* components[5];
    const char* learned_logic[8];
} omni_ffi_diagnostics_t;

static inline omni_ffi_diagnostics_t omni_ffi_diagnostics(void) {
    omni_ffi_diagnostics_t d = {
        .engine = "OmniFFIBridgeEngine",
        .layer = "C System",
        .components = {
            "omni_handle_t", "omni_callback_registry_t",
            "omni_version_header_t", "omni_strview_t",
            "omni_bytebuf_t"
        },
        .learned_logic = {
            "opaque-handle-type-safety",
            "callback-registry-dispatch",
            "versioned-struct-abi-compat",
            "string-view-non-owning-slice",
            "byte-buffer-growable-append",
            "magic-number-validation",
            "destructor-cleanup-function",
            "container-of-offset-trick"
        }
    };
    return d;
}

#ifdef __cplusplus
}
#endif

#endif /* OMNI_FFI_BRIDGE_ENGINE_H */
