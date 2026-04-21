/* ===========================================================================
 * OMNI HASH TABLE ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.7)
 * ===========================================================================
 * Absorbed From  : Python dict (compact+ordered) + Robin Hood hashing
 * Logic Inherited: C / System Layer (Open-Addressing Robin Hood Hash Table)
 * Domain Layer   : System (C Core)
 * ===========================================================================
 *
 * By studying CPython's dict implementation and Robin Hood hashing from
 * Rust's hashbrown, Mother learned that open-addressing with Robin Hood
 * probe-sequence balancing achieves better cache performance than chaining:
 *   1. All entries live in a contiguous array (cache-friendly)
 *   2. Robin Hood: when inserting, if the probe distance of the new key
 *      exceeds the probe distance of the existing key at that slot,
 *      SWAP them — this bounds maximum probe length to O(log N)
 *   3. FNV-1a hash: fast, well-distributed, no external dependency
 *
 * C provides direct memory control needed for the contiguous bucket array
 * and manual resize logic. RAII patterns are simulated with explicit
 * init/destroy lifecycle functions.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* ---- Configuration ---- */

#define OMNI_HT_INITIAL_CAPACITY   16
#define OMNI_HT_LOAD_FACTOR_MAX    0.75
#define OMNI_HT_GROWTH_FACTOR      2
#define OMNI_HT_MAX_KEY_LEN        256
#define OMNI_HT_MAX_VALUE_LEN      4096

/* ---- Bucket State ---- */

typedef enum {
    BUCKET_EMPTY    = 0,
    BUCKET_OCCUPIED = 1,
    BUCKET_DELETED  = 2   /* Tombstone for lazy deletion */
} BucketState;

/* ---- Bucket Entry ---- */

typedef struct {
    BucketState state;
    uint64_t    hash;
    uint32_t    probe_distance;  /* Distance from ideal position */
    char        key[OMNI_HT_MAX_KEY_LEN];
    char        value[OMNI_HT_MAX_VALUE_LEN];
} Bucket;

/* ---- Hash Table ---- */

typedef struct {
    Bucket*   buckets;
    size_t    capacity;
    size_t    size;        /* Number of occupied entries */
    size_t    tombstones;  /* Number of deleted entries */
    /* Statistics */
    uint64_t  total_inserts;
    uint64_t  total_lookups;
    uint64_t  total_deletes;
    uint64_t  total_collisions;
    uint64_t  total_resizes;
    uint64_t  max_probe_distance;
} OmniHashTableEngine;

/* ---- FNV-1a Hash Function ---- */

static uint64_t fnv1a_hash(const char* key) {
    uint64_t hash = 14695981039346656037ULL;  /* FNV offset basis */
    while (*key) {
        hash ^= (uint64_t)(unsigned char)(*key);
        hash *= 1099511628211ULL;  /* FNV prime */
        key++;
    }
    return hash;
}

/* ---- Lifecycle ---- */

/**
 * Initialize a new hash table with the given initial capacity.
 * Returns 0 on success, -1 on allocation failure.
 */
int omni_ht_init(OmniHashTableEngine* ht, size_t initial_capacity) {
    if (initial_capacity == 0) initial_capacity = OMNI_HT_INITIAL_CAPACITY;

    /* Round up to power of 2 for fast modulo via bitmask */
    size_t cap = 1;
    while (cap < initial_capacity) cap <<= 1;

    ht->buckets = (Bucket*)calloc(cap, sizeof(Bucket));
    if (!ht->buckets) return -1;

    ht->capacity = cap;
    ht->size = 0;
    ht->tombstones = 0;
    ht->total_inserts = 0;
    ht->total_lookups = 0;
    ht->total_deletes = 0;
    ht->total_collisions = 0;
    ht->total_resizes = 0;
    ht->max_probe_distance = 0;

    return 0;
}

/**
 * Destroy the hash table, freeing all memory.
 */
void omni_ht_destroy(OmniHashTableEngine* ht) {
    if (ht->buckets) {
        free(ht->buckets);
        ht->buckets = NULL;
    }
    ht->capacity = 0;
    ht->size = 0;
}

/* ---- Internal: Resize ---- */

static int omni_ht_resize(OmniHashTableEngine* ht, size_t new_capacity) {
    Bucket* old_buckets = ht->buckets;
    size_t  old_capacity = ht->capacity;

    ht->buckets = (Bucket*)calloc(new_capacity, sizeof(Bucket));
    if (!ht->buckets) {
        ht->buckets = old_buckets;  /* Restore on failure */
        return -1;
    }

    ht->capacity = new_capacity;
    ht->size = 0;
    ht->tombstones = 0;
    ht->total_resizes++;

    /* Re-insert all occupied entries into new table */
    for (size_t i = 0; i < old_capacity; i++) {
        if (old_buckets[i].state == BUCKET_OCCUPIED) {
            /* Direct insert without recursion check — we know there's room */
            uint64_t hash = old_buckets[i].hash;
            size_t idx = hash & (new_capacity - 1);
            uint32_t probe = 0;

            /* Build entry to insert */
            Bucket entry;
            entry.state = BUCKET_OCCUPIED;
            entry.hash = hash;
            entry.probe_distance = 0;
            strncpy(entry.key, old_buckets[i].key, OMNI_HT_MAX_KEY_LEN - 1);
            entry.key[OMNI_HT_MAX_KEY_LEN - 1] = '\0';
            strncpy(entry.value, old_buckets[i].value, OMNI_HT_MAX_VALUE_LEN - 1);
            entry.value[OMNI_HT_MAX_VALUE_LEN - 1] = '\0';

            while (1) {
                Bucket* slot = &ht->buckets[idx];

                if (slot->state != BUCKET_OCCUPIED) {
                    entry.probe_distance = probe;
                    *slot = entry;
                    ht->size++;
                    break;
                }

                /* Robin Hood: steal from rich (low probe) to give to poor (high probe) */
                if (probe > slot->probe_distance) {
                    Bucket tmp = *slot;
                    entry.probe_distance = probe;
                    *slot = entry;
                    entry = tmp;
                    probe = entry.probe_distance;
                }

                probe++;
                idx = (idx + 1) & (new_capacity - 1);
            }
        }
    }

    free(old_buckets);
    return 0;
}

/* ---- Public API ---- */

/**
 * Insert or update a key-value pair.
 * Returns 0 on success (insert), 1 on success (update), -1 on error.
 */
int omni_ht_put(OmniHashTableEngine* ht, const char* key, const char* value) {
    /* Check load factor and resize if needed */
    double load = (double)(ht->size + ht->tombstones) / (double)ht->capacity;
    if (load >= OMNI_HT_LOAD_FACTOR_MAX) {
        if (omni_ht_resize(ht, ht->capacity * OMNI_HT_GROWTH_FACTOR) != 0) {
            return -1;
        }
    }

    uint64_t hash = fnv1a_hash(key);
    size_t idx = hash & (ht->capacity - 1);
    uint32_t probe = 0;

    /* Build entry */
    Bucket entry;
    entry.state = BUCKET_OCCUPIED;
    entry.hash = hash;
    entry.probe_distance = 0;
    strncpy(entry.key, key, OMNI_HT_MAX_KEY_LEN - 1);
    entry.key[OMNI_HT_MAX_KEY_LEN - 1] = '\0';
    strncpy(entry.value, value, OMNI_HT_MAX_VALUE_LEN - 1);
    entry.value[OMNI_HT_MAX_VALUE_LEN - 1] = '\0';

    ht->total_inserts++;

    while (1) {
        Bucket* slot = &ht->buckets[idx];

        /* Empty or tombstone — insert here */
        if (slot->state == BUCKET_EMPTY || slot->state == BUCKET_DELETED) {
            if (slot->state == BUCKET_DELETED) ht->tombstones--;
            entry.probe_distance = probe;
            *slot = entry;
            ht->size++;
            if (probe > ht->max_probe_distance) ht->max_probe_distance = probe;
            return 0;
        }

        /* Key exists — update value */
        if (slot->state == BUCKET_OCCUPIED &&
            slot->hash == hash &&
            strncmp(slot->key, key, OMNI_HT_MAX_KEY_LEN) == 0) {
            strncpy(slot->value, value, OMNI_HT_MAX_VALUE_LEN - 1);
            slot->value[OMNI_HT_MAX_VALUE_LEN - 1] = '\0';
            return 1;
        }

        /* Robin Hood swap: rich gives to poor */
        if (probe > slot->probe_distance) {
            Bucket tmp = *slot;
            entry.probe_distance = probe;
            *slot = entry;
            entry = tmp;
            probe = entry.probe_distance;
            ht->total_collisions++;
        }

        probe++;
        idx = (idx + 1) & (ht->capacity - 1);
        ht->total_collisions++;
    }
}

/**
 * Look up a key. Returns pointer to value string, or NULL if not found.
 * The returned pointer is valid until the next insert/delete/resize.
 */
const char* omni_ht_get(OmniHashTableEngine* ht, const char* key) {
    ht->total_lookups++;

    uint64_t hash = fnv1a_hash(key);
    size_t idx = hash & (ht->capacity - 1);
    uint32_t probe = 0;

    while (1) {
        Bucket* slot = &ht->buckets[idx];

        if (slot->state == BUCKET_EMPTY) {
            return NULL;  /* Key not found */
        }

        if (slot->state == BUCKET_OCCUPIED &&
            slot->hash == hash &&
            strncmp(slot->key, key, OMNI_HT_MAX_KEY_LEN) == 0) {
            return slot->value;
        }

        /* Robin Hood optimization: if our probe distance exceeds
         * the existing entry's, the key cannot be further ahead */
        if (slot->state == BUCKET_OCCUPIED && probe > slot->probe_distance) {
            return NULL;
        }

        probe++;
        idx = (idx + 1) & (ht->capacity - 1);

        /* Safety: don't loop forever */
        if (probe >= ht->capacity) return NULL;
    }
}

/**
 * Delete a key. Returns 0 on success, -1 if key not found.
 * Uses tombstone (lazy) deletion to maintain probe chains.
 */
int omni_ht_delete(OmniHashTableEngine* ht, const char* key) {
    ht->total_deletes++;

    uint64_t hash = fnv1a_hash(key);
    size_t idx = hash & (ht->capacity - 1);
    uint32_t probe = 0;

    while (1) {
        Bucket* slot = &ht->buckets[idx];

        if (slot->state == BUCKET_EMPTY) {
            return -1;
        }

        if (slot->state == BUCKET_OCCUPIED &&
            slot->hash == hash &&
            strncmp(slot->key, key, OMNI_HT_MAX_KEY_LEN) == 0) {
            slot->state = BUCKET_DELETED;
            ht->size--;
            ht->tombstones++;
            return 0;
        }

        if (slot->state == BUCKET_OCCUPIED && probe > slot->probe_distance) {
            return -1;
        }

        probe++;
        idx = (idx + 1) & (ht->capacity - 1);
        if (probe >= ht->capacity) return -1;
    }
}

/**
 * Check if a key exists.
 */
int omni_ht_contains(OmniHashTableEngine* ht, const char* key) {
    return omni_ht_get(ht, key) != NULL ? 1 : 0;
}

/**
 * Number of entries.
 */
size_t omni_ht_size(const OmniHashTableEngine* ht) {
    return ht->size;
}

/**
 * Clear all entries.
 */
void omni_ht_clear(OmniHashTableEngine* ht) {
    memset(ht->buckets, 0, ht->capacity * sizeof(Bucket));
    ht->size = 0;
    ht->tombstones = 0;
}

/* ---- Diagnostics ---- */

typedef struct {
    const char* engine;
    const char* layer;
    size_t      capacity;
    size_t      size;
    size_t      tombstones;
    double      load_factor;
    uint64_t    max_probe_distance;
    uint64_t    total_inserts;
    uint64_t    total_lookups;
    uint64_t    total_deletes;
    uint64_t    total_collisions;
    uint64_t    total_resizes;
} OmniHTDiagnostics;

OmniHTDiagnostics omni_ht_diagnostics(const OmniHashTableEngine* ht) {
    OmniHTDiagnostics d;
    d.engine = "OmniHashTableEngine";
    d.layer = "C System";
    d.capacity = ht->capacity;
    d.size = ht->size;
    d.tombstones = ht->tombstones;
    d.load_factor = (ht->capacity > 0)
        ? (double)ht->size / (double)ht->capacity
        : 0.0;
    d.max_probe_distance = ht->max_probe_distance;
    d.total_inserts = ht->total_inserts;
    d.total_lookups = ht->total_lookups;
    d.total_deletes = ht->total_deletes;
    d.total_collisions = ht->total_collisions;
    d.total_resizes = ht->total_resizes;
    return d;
}

void omni_ht_print_diagnostics(const OmniHashTableEngine* ht) {
    OmniHTDiagnostics d = omni_ht_diagnostics(ht);
    printf("=== %s (%s) ===\n", d.engine, d.layer);
    printf("Capacity:           %zu\n", d.capacity);
    printf("Size:               %zu\n", d.size);
    printf("Tombstones:         %zu\n", d.tombstones);
    printf("Load Factor:        %.2f%%\n", d.load_factor * 100.0);
    printf("Max Probe Distance: %llu\n", (unsigned long long)d.max_probe_distance);
    printf("Total Inserts:      %llu\n", (unsigned long long)d.total_inserts);
    printf("Total Lookups:      %llu\n", (unsigned long long)d.total_lookups);
    printf("Total Deletes:      %llu\n", (unsigned long long)d.total_deletes);
    printf("Total Collisions:   %llu\n", (unsigned long long)d.total_collisions);
    printf("Total Resizes:      %llu\n", (unsigned long long)d.total_resizes);
    printf("Learned Logic:      fnv1a-hash, robin-hood-probe-balancing, "
           "power-of-two-bitmask, tombstone-lazy-deletion, "
           "contiguous-bucket-cache-locality\n");
}
