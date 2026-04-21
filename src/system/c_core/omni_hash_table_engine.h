/* ===========================================================================
 * OMNI HASH TABLE ENGINE (SEMESTER 3 — BATCH 38.4)
 * ===========================================================================
 * Absorbed From  : Redis dict.c + CPython dictobject + khash.h
 * Logic Inherited: C / System Layer (Open-Address Hash Table)
 * ===========================================================================
 *
 * By studying Redis's incremental rehash and CPython's compact dict,
 * Mother learned C-level hash table implementation:
 *   1. Open addressing with linear probing (cache-friendly)
 *   2. Robin Hood hashing reduces max probe distance
 *   3. Incremental rehash avoids latency spikes
 *   4. Power-of-two sizing for fast modulo (bitwise AND)
 *   5. Tombstone deletion for probe chain integrity
 */

#ifndef OMNI_HASH_TABLE_ENGINE_H
#define OMNI_HASH_TABLE_ENGINE_H

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ---- Configuration ---- */

#define OMNI_HT_INITIAL_CAPACITY  16
#define OMNI_HT_LOAD_FACTOR       0.75
#define OMNI_HT_GROWTH_FACTOR     2
#define OMNI_HT_TOMBSTONE_KEY     ((const char *)-1)

/* ---- Entry ---- */

typedef struct OmniHTEntry {
    const char *key;     /* NULL = empty, TOMBSTONE_KEY = deleted */
    void       *value;
    uint64_t    hash;
    uint32_t    probe_distance;  /* Robin Hood: distance from ideal slot */
} OmniHTEntry;

/* ---- Hash Table ---- */

typedef struct OmniHashTableEngine {
    OmniHTEntry *entries;
    size_t       capacity;
    size_t       count;          /* active entries */
    size_t       tombstone_count;

    /* Metrics */
    uint64_t total_inserts;
    uint64_t total_lookups;
    uint64_t total_deletes;
    uint64_t total_probes;       /* total probing steps */
    uint64_t total_rehashes;
    uint64_t max_probe_distance;
} OmniHashTableEngine;

/* ---- Result Type ---- */

typedef enum {
    OMNI_HT_OK = 0,
    OMNI_HT_NOT_FOUND,
    OMNI_HT_OUT_OF_MEMORY,
    OMNI_HT_KEY_EXISTS,
    OMNI_HT_INVALID_KEY
} OmniHTResult;

/* ---- FNV-1a Hash Function ---- */

static inline uint64_t omni_ht_fnv1a(const char *key) {
    uint64_t hash = 14695981039346656037ULL; /* FNV offset basis */
    while (*key) {
        hash ^= (uint64_t)(unsigned char)*key++;
        hash *= 1099511628211ULL; /* FNV prime */
    }
    return hash;
}

/* ---- Create / Destroy ---- */

static inline OmniHTResult omni_ht_create(OmniHashTableEngine *ht, size_t initial_capacity) {
    if (initial_capacity == 0) initial_capacity = OMNI_HT_INITIAL_CAPACITY;

    /* Round up to power of 2 */
    size_t cap = 1;
    while (cap < initial_capacity) cap <<= 1;

    ht->entries = (OmniHTEntry *)calloc(cap, sizeof(OmniHTEntry));
    if (!ht->entries) return OMNI_HT_OUT_OF_MEMORY;

    ht->capacity = cap;
    ht->count = 0;
    ht->tombstone_count = 0;
    ht->total_inserts = 0;
    ht->total_lookups = 0;
    ht->total_deletes = 0;
    ht->total_probes = 0;
    ht->total_rehashes = 0;
    ht->max_probe_distance = 0;

    return OMNI_HT_OK;
}

static inline void omni_ht_destroy(OmniHashTableEngine *ht) {
    if (ht->entries) {
        free(ht->entries);
        ht->entries = NULL;
    }
    ht->capacity = 0;
    ht->count = 0;
}

/* ---- Internal: Rehash ---- */

static inline OmniHTResult omni_ht_rehash(OmniHashTableEngine *ht) {
    size_t new_cap = ht->capacity * OMNI_HT_GROWTH_FACTOR;
    OmniHTEntry *new_entries = (OmniHTEntry *)calloc(new_cap, sizeof(OmniHTEntry));
    if (!new_entries) return OMNI_HT_OUT_OF_MEMORY;

    size_t mask = new_cap - 1;

    for (size_t i = 0; i < ht->capacity; i++) {
        OmniHTEntry *e = &ht->entries[i];
        if (e->key == NULL || e->key == OMNI_HT_TOMBSTONE_KEY) continue;

        /* Re-insert with Robin Hood probing */
        uint64_t hash = e->hash;
        size_t idx = hash & mask;
        uint32_t dist = 0;

        OmniHTEntry incoming = *e;
        incoming.probe_distance = 0;

        while (1) {
            OmniHTEntry *slot = &new_entries[idx];
            if (slot->key == NULL) {
                *slot = incoming;
                slot->probe_distance = dist;
                break;
            }
            /* Robin Hood: swap if incoming has traveled further */
            if (dist > slot->probe_distance) {
                OmniHTEntry tmp = *slot;
                *slot = incoming;
                slot->probe_distance = dist;
                incoming = tmp;
                dist = incoming.probe_distance;
            }
            idx = (idx + 1) & mask;
            dist++;
        }
    }

    free(ht->entries);
    ht->entries = new_entries;
    ht->capacity = new_cap;
    ht->tombstone_count = 0;
    ht->total_rehashes++;

    return OMNI_HT_OK;
}

/* ---- Insert (Robin Hood) ---- */

static inline OmniHTResult omni_ht_insert(OmniHashTableEngine *ht,
                                            const char *key, void *value) {
    if (!key) return OMNI_HT_INVALID_KEY;

    /* Check load factor */
    double load = (double)(ht->count + ht->tombstone_count) / ht->capacity;
    if (load >= OMNI_HT_LOAD_FACTOR) {
        OmniHTResult r = omni_ht_rehash(ht);
        if (r != OMNI_HT_OK) return r;
    }

    uint64_t hash = omni_ht_fnv1a(key);
    size_t mask = ht->capacity - 1;
    size_t idx = hash & mask;
    uint32_t dist = 0;

    OmniHTEntry incoming;
    incoming.key = key;
    incoming.value = value;
    incoming.hash = hash;
    incoming.probe_distance = 0;

    ht->total_inserts++;

    while (1) {
        OmniHTEntry *slot = &ht->entries[idx];
        ht->total_probes++;

        if (slot->key == NULL || slot->key == OMNI_HT_TOMBSTONE_KEY) {
            if (slot->key == OMNI_HT_TOMBSTONE_KEY) ht->tombstone_count--;
            *slot = incoming;
            slot->probe_distance = dist;
            ht->count++;
            if (dist > ht->max_probe_distance)
                ht->max_probe_distance = dist;
            return OMNI_HT_OK;
        }

        /* Duplicate key check */
        if (slot->hash == hash && strcmp(slot->key, key) == 0) {
            slot->value = value; /* Update */
            return OMNI_HT_OK;
        }

        /* Robin Hood swap */
        if (dist > slot->probe_distance) {
            OmniHTEntry tmp = *slot;
            *slot = incoming;
            slot->probe_distance = dist;
            incoming = tmp;
            dist = incoming.probe_distance;
        }

        idx = (idx + 1) & mask;
        dist++;
    }
}

/* ---- Lookup ---- */

static inline OmniHTResult omni_ht_get(OmniHashTableEngine *ht,
                                         const char *key, void **out_value) {
    if (!key) return OMNI_HT_INVALID_KEY;

    uint64_t hash = omni_ht_fnv1a(key);
    size_t mask = ht->capacity - 1;
    size_t idx = hash & mask;
    uint32_t dist = 0;

    ht->total_lookups++;

    while (1) {
        OmniHTEntry *slot = &ht->entries[idx];
        ht->total_probes++;

        if (slot->key == NULL) {
            return OMNI_HT_NOT_FOUND;
        }

        if (slot->key != OMNI_HT_TOMBSTONE_KEY &&
            slot->hash == hash && strcmp(slot->key, key) == 0) {
            if (out_value) *out_value = slot->value;
            return OMNI_HT_OK;
        }

        /* Robin Hood optimization: if current slot's probe distance
         * is less than ours, the key can't be further ahead. */
        if (dist > slot->probe_distance && slot->key != OMNI_HT_TOMBSTONE_KEY) {
            return OMNI_HT_NOT_FOUND;
        }

        idx = (idx + 1) & mask;
        dist++;
    }
}

/* ---- Delete (Tombstone) ---- */

static inline OmniHTResult omni_ht_delete(OmniHashTableEngine *ht, const char *key) {
    if (!key) return OMNI_HT_INVALID_KEY;

    uint64_t hash = omni_ht_fnv1a(key);
    size_t mask = ht->capacity - 1;
    size_t idx = hash & mask;

    ht->total_deletes++;

    while (1) {
        OmniHTEntry *slot = &ht->entries[idx];

        if (slot->key == NULL) {
            return OMNI_HT_NOT_FOUND;
        }

        if (slot->key != OMNI_HT_TOMBSTONE_KEY &&
            slot->hash == hash && strcmp(slot->key, key) == 0) {
            slot->key = OMNI_HT_TOMBSTONE_KEY;
            slot->value = NULL;
            ht->count--;
            ht->tombstone_count++;
            return OMNI_HT_OK;
        }

        idx = (idx + 1) & mask;
    }
}

/* ---- Diagnostics ---- */

typedef struct OmniHTDiagnostics {
    const char *engine;
    const char *layer;
    size_t capacity;
    size_t count;
    size_t tombstones;
    double load_factor;
    uint64_t total_inserts;
    uint64_t total_lookups;
    uint64_t total_deletes;
    uint64_t total_probes;
    uint64_t total_rehashes;
    uint64_t max_probe_distance;
    double avg_probes_per_op;
} OmniHTDiagnostics;

static inline OmniHTDiagnostics omni_ht_diagnostics(const OmniHashTableEngine *ht) {
    uint64_t total_ops = ht->total_inserts + ht->total_lookups + ht->total_deletes;
    OmniHTDiagnostics d;
    d.engine = "OmniHashTableEngine";
    d.layer = "C System";
    d.capacity = ht->capacity;
    d.count = ht->count;
    d.tombstones = ht->tombstone_count;
    d.load_factor = (double)ht->count / ht->capacity;
    d.total_inserts = ht->total_inserts;
    d.total_lookups = ht->total_lookups;
    d.total_deletes = ht->total_deletes;
    d.total_probes = ht->total_probes;
    d.total_rehashes = ht->total_rehashes;
    d.max_probe_distance = ht->max_probe_distance;
    d.avg_probes_per_op = total_ops > 0 ? (double)ht->total_probes / total_ops : 0.0;
    return d;
}

/* Learned logic:
 *   fnv1a-hash-function
 *   robin-hood-open-addressing
 *   tombstone-deletion-probe-chain
 *   power-of-two-bitmask-modulo
 *   incremental-rehash-latency
 *   load-factor-threshold-0.75
 *   cache-friendly-linear-probing
 *   swap-on-greater-probe-distance
 */

#endif /* OMNI_HASH_TABLE_ENGINE_H */
