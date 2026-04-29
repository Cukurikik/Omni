#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define OMNI_MAX_CACHE_ENTRIES 50000

typedef struct CacheNode {
    char key[64];
    double score;
    struct CacheNode* prev;
    struct CacheNode* next;
} CacheNode;

typedef struct {
    CacheNode* head;
    CacheNode* tail;
    int count;
    int capacity;
} LruCache;

typedef struct {
    bool is_ok;
    double payload;
    const char* error;
} OmniResult_Double;

LruCache* llmrank_cache_init(int capacity) {
    if (capacity > OMNI_MAX_CACHE_ENTRIES) capacity = OMNI_MAX_CACHE_ENTRIES;
    LruCache* cache = (LruCache*)malloc(sizeof(LruCache));
    if (!cache) return NULL;
    cache->head = NULL;
    cache->tail = NULL;
    cache->count = 0;
    cache->capacity = capacity;
    return cache;
}

OmniResult_Double llmrank_cache_get(LruCache* cache, const char* key) {
    OmniResult_Double res = {0};
    if (!cache || !key) {
        res.is_ok = false;
        res.error = "OMNI_ERR: Invalid cache or key pointers.";
        return res;
    }

    CacheNode* curr = cache->head;
    while (curr) {
        if (strncmp(curr->key, key, 64) == 0) {
            // Move to head
            if (curr != cache->head) {
                if (curr->prev) curr->prev->next = curr->next;
                if (curr->next) curr->next->prev = curr->prev;
                if (curr == cache->tail) cache->tail = curr->prev;
                
                curr->next = cache->head;
                curr->prev = NULL;
                cache->head->prev = curr;
                cache->head = curr;
            }
            res.is_ok = true;
            res.payload = curr->score;
            return res;
        }
        curr = curr->next;
    }
    
    res.is_ok = false;
    res.error = "OMNI_CACHE_MISS: Key not found.";
    return res;
}
