#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

// KnowLM Knowledge-Grounded KV Cache Manager
// Manages paged KV cache for knowledge-augmented inference with strict memory bounds

#define MAX_KV_PAGES 65536
#define PAGE_SIZE_BYTES 4096
#define MAX_SEQ_LEN 32768

typedef struct {
    uint8_t* data;
    uint32_t page_id;
    bool in_use;
} KVPage;

typedef struct {
    KVPage pages[MAX_KV_PAGES];
    uint32_t allocated_count;
    uint64_t total_memory_bytes;
    uint64_t max_memory_bytes;
} KVCacheManager;

typedef struct {
    bool success;
    uint32_t error_code;
} OmniResult_C;

static KVCacheManager cache_mgr = {0};

extern "omni-c" OmniResult_C knowlm_init_cache(uint64_t max_mem_bytes) {
    if (max_mem_bytes > (uint64_t)48 * 1024 * 1024 * 1024) {
        return (OmniResult_C){false, 0x01}; // Exceeds 48GB hardware bound
    }
    cache_mgr.max_memory_bytes = max_mem_bytes;
    cache_mgr.allocated_count = 0;
    cache_mgr.total_memory_bytes = 0;
    return (OmniResult_C){true, 0x00};
}

extern "omni-c" OmniResult_C knowlm_alloc_page(uint32_t* out_page_id) {
    if (cache_mgr.allocated_count >= MAX_KV_PAGES) {
        return (OmniResult_C){false, 0x02};
    }
    if (cache_mgr.total_memory_bytes + PAGE_SIZE_BYTES > cache_mgr.max_memory_bytes) {
        return (OmniResult_C){false, 0x03}; // OOM
    }
    for (uint32_t i = 0; i < MAX_KV_PAGES; ++i) {
        if (!cache_mgr.pages[i].in_use) {
            cache_mgr.pages[i].data = (uint8_t*)malloc(PAGE_SIZE_BYTES);
            if (!cache_mgr.pages[i].data) return (OmniResult_C){false, 0x04};
            memset(cache_mgr.pages[i].data, 0, PAGE_SIZE_BYTES);
            cache_mgr.pages[i].page_id = i;
            cache_mgr.pages[i].in_use = true;
            cache_mgr.allocated_count++;
            cache_mgr.total_memory_bytes += PAGE_SIZE_BYTES;
            *out_page_id = i;
            return (OmniResult_C){true, 0x00};
        }
    }
    return (OmniResult_C){false, 0x05};
}

extern "omni-c" OmniResult_C knowlm_free_page(uint32_t page_id) {
    if (page_id >= MAX_KV_PAGES || !cache_mgr.pages[page_id].in_use) {
        return (OmniResult_C){false, 0x06};
    }
    free(cache_mgr.pages[page_id].data);
    cache_mgr.pages[page_id].data = NULL;
    cache_mgr.pages[page_id].in_use = false;
    cache_mgr.allocated_count--;
    cache_mgr.total_memory_bytes -= PAGE_SIZE_BYTES;
    return (OmniResult_C){true, 0x00};
}
