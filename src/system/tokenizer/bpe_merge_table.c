// @omni-layer System | @omni-source openai/tiktoken | @omni-lang C
// @omni-description BPE merge table: hash-based pair lookup for O(1) merge
// operation during tokenization encoding.
#include <stdlib.h>
#include <string.h>

#define MERGE_TABLE_SIZE 65536
#define MAX_MERGES 32768

typedef struct {
    unsigned int pair_hash;
    int left, right;
    int merged_id;
    int valid;
} MergeEntry;

typedef struct {
    MergeEntry table[MERGE_TABLE_SIZE];
    int n_merges;
    int next_id;
} BPEMergeTable;

static unsigned int pair_hash(int left, int right) {
    unsigned int h = (unsigned int)left * 2654435761u;
    h ^= (unsigned int)right * 2246822519u;
    return h % MERGE_TABLE_SIZE;
}

void bpe_init(BPEMergeTable *t) {
    memset(t, 0, sizeof(BPEMergeTable));
    t->next_id = 256;
}

int bpe_add_merge(BPEMergeTable *t, int left, int right) {
    if (t->n_merges >= MAX_MERGES) return -1;
    unsigned int h = pair_hash(left, right);
    unsigned int idx = h;
    for (int i = 0; i < MERGE_TABLE_SIZE; i++) {
        idx = (h + i) % MERGE_TABLE_SIZE;
        if (!t->table[idx].valid) break;
    }
    t->table[idx].pair_hash = h;
    t->table[idx].left = left;
    t->table[idx].right = right;
    t->table[idx].merged_id = t->next_id;
    t->table[idx].valid = 1;
    t->n_merges++;
    return t->next_id++;
}

int bpe_lookup(const BPEMergeTable *t, int left, int right) {
    unsigned int h = pair_hash(left, right);
    for (int i = 0; i < MERGE_TABLE_SIZE; i++) {
        unsigned int idx = (h + i) % MERGE_TABLE_SIZE;
        if (!t->table[idx].valid) return -1;
        if (t->table[idx].left == left && t->table[idx].right == right)
            return t->table[idx].merged_id;
    }
    return -1;
}

int bpe_encode(const BPEMergeTable *t, int *ids, int len) {
    if (!t || !ids || len <= 0) return len;
    int changed = 1;
    while (changed) {
        changed = 0;
        for (int i = 0; i < len - 1; i++) {
            int merged = bpe_lookup(t, ids[i], ids[i+1]);
            if (merged >= 0) {
                ids[i] = merged;
                memmove(&ids[i+1], &ids[i+2], (len-i-2)*sizeof(int));
                len--;
                changed = 1;
                break;
            }
        }
    }
    return len;
}
