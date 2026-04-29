// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Redis LRU Cache (OMNI Zero-Mock Implementation)
// Implements core pointer logic for LRU eviction in C.

#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    void* value;
    char* error;
    bool is_ok;
} ResultPtr;

ResultPtr OkPtr(void* val) {
    ResultPtr r = {val, NULL, true};
    return r;
}

ResultPtr ErrPtr(const char* err) {
    char* err_cpy = strdup(err);
    ResultPtr r = {NULL, err_cpy, false};
    return r;
}

// Doubly Linked List Node
typedef struct Node {
    char* key;
    char* value;
    struct Node* prev;
    struct Node* next;
} Node;

typedef struct {
    int capacity;
    int size;
    Node* head;
    Node* tail;
} RedisLRU;

ResultPtr create_redis_lru(int capacity) {
    if (capacity <= 0) {
        return ErrPtr("Capacity must be positive");
    }
    RedisLRU* cache = (RedisLRU*)malloc(sizeof(RedisLRU));
    cache->capacity = capacity;
    cache->size = 0;
    cache->head = NULL;
    cache->tail = NULL;
    return OkPtr(cache);
}

// Moves a node to the front of the queue
void _lru_move_to_front(RedisLRU* cache, Node* node) {
    if (cache->head == node) return; // Already at head

    // Detach
    if (node->prev) node->prev->next = node->next;
    if (node->next) node->next->prev = node->prev;
    if (cache->tail == node) cache->tail = node->prev;

    // Attach to head
    node->next = cache->head;
    node->prev = NULL;
    if (cache->head) cache->head->prev = node;
    cache->head = node;
    
    if (cache->tail == NULL) cache->tail = node;
}

ResultPtr redis_lru_set(RedisLRU* cache, const char* key, const char* value) {
    if (!cache || !key || !value) return ErrPtr("Null pointers passed to set");
    
    // Check if exists (Linear scan since we don't have a hash map in this zero-mock pure C logic.
    // In full engine, combined with HashTable)
    Node* current = cache->head;
    while (current) {
        if (strcmp(current->key, key) == 0) {
            free(current->value);
            current->value = strdup(value);
            _lru_move_to_front(cache, current);
            return OkPtr(NULL);
        }
        current = current->next;
    }
    
    // Add new
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->key = strdup(key);
    new_node->value = strdup(value);
    new_node->next = cache->head;
    new_node->prev = NULL;
    
    if (cache->head) cache->head->prev = new_node;
    cache->head = new_node;
    if (!cache->tail) cache->tail = new_node;
    
    cache->size++;
    
    // Evict
    if (cache->size > cache->capacity) {
        Node* evict = cache->tail;
        cache->tail = evict->prev;
        if (cache->tail) cache->tail->next = NULL;
        
        free(evict->key);
        free(evict->value);
        free(evict);
        cache->size--;
    }
    
    return OkPtr(NULL);
}
