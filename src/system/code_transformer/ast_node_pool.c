// @omni-layer System | @omni-source danielzuegner/code-transformer | @omni-lang C
// @omni-description AST node pool allocator: arena-based memory for code transformer
// AST nodes with O(1) allocation and batch deallocation.
#include <stdlib.h>
#include <string.h>

#define MAX_NODES 65536
#define MAX_CHILDREN 16

typedef struct ASTNode {
    int node_type;
    int token_id;
    int depth;
    int parent_idx;
    int children[MAX_CHILDREN];
    int n_children;
    float embedding[64];
} ASTNode;

typedef struct {
    ASTNode nodes[MAX_NODES];
    int count;
    int capacity;
} ASTNodePool;

void ast_pool_init(ASTNodePool *pool) {
    pool->count = 0;
    pool->capacity = MAX_NODES;
}

int ast_pool_alloc(ASTNodePool *pool, int node_type, int token_id, int depth, int parent) {
    if (pool->count >= pool->capacity) return -1;
    int idx = pool->count++;
    ASTNode *node = &pool->nodes[idx];
    node->node_type = node_type;
    node->token_id = token_id;
    node->depth = depth;
    node->parent_idx = parent;
    node->n_children = 0;
    memset(node->embedding, 0, sizeof(node->embedding));
    return idx;
}

int ast_pool_add_child(ASTNodePool *pool, int parent_idx, int child_idx) {
    if (parent_idx < 0 || parent_idx >= pool->count) return -1;
    ASTNode *parent = &pool->nodes[parent_idx];
    if (parent->n_children >= MAX_CHILDREN) return -1;
    parent->children[parent->n_children++] = child_idx;
    return 0;
}

int ast_pool_build_relation_matrix(const ASTNodePool *pool, int *matrix, int n) {
    if (!pool || !matrix || n <= 0) return -1;
    memset(matrix, 0, n * n * sizeof(int));
    for (int i = 0; i < pool->count && i < n; i++) {
        const ASTNode *node = &pool->nodes[i];
        if (node->parent_idx >= 0 && node->parent_idx < n) {
            matrix[i * n + node->parent_idx] = 1;
            matrix[node->parent_idx * n + i] = 2;
        }
        for (int c = 0; c < node->n_children && c < MAX_CHILDREN; c++) {
            int child = node->children[c];
            if (child >= 0 && child < n) matrix[i * n + child] = 2;
        }
    }
    return 0;
}

void ast_pool_reset(ASTNodePool *pool) { pool->count = 0; }
