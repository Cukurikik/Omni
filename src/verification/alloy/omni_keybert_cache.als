// OMNI Framework - Alloy Model for KeyBERT Cache Consistency
// Verifies that the caching mechanism does not serve stale or incorrect NLP data

module omni/keybert_cache

sig Document {}
sig Keywords {}

sig Cache {
    entries: Document -> lone Keywords
}

// Operation: Add to cache
pred put_cache[c, c': Cache, d: Document, k: Keywords] {
    c'.entries = c.entries ++ (d -> k)
}

// Operation: Evict from cache
pred evict_cache[c, c': Cache, d: Document] {
    c'.entries = c.entries - (d -> Keywords)
}

// Property: Consistency after Put
assert PutMaintainsConsistency {
    all c, c': Cache, d: Document, k: Keywords |
        put_cache[c, c', d, k] => c'.entries[d] = k
}

// Property: No ghost entries after Evict
assert EvictRemovesData {
    all c, c': Cache, d: Document |
        evict_cache[c, c', d] => no c'.entries[d]
}

check PutMaintainsConsistency for 5
check EvictRemovesData for 5
