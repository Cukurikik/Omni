// OMNI MOTHER — SEMESTER 13 REMEDIATION
// SQL — Business Layer (OMNI Zero-Mock Implementation)
// Implements deterministic B-Tree index range scan cost estimation engine.
// Absorbs patterns from: PostgreSQL query planner, MySQL optimizer

#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    unsigned long long total_rows;
    unsigned long long distinct_values;
    int tree_height;
    int page_size_bytes;
    int row_size_bytes;
} BTreeIndexStats;

typedef struct {
    double estimated_rows;
    double estimated_io_cost;
    double estimated_cpu_cost;
    double total_cost;
    int use_index_scan;      // 1 = index scan, 0 = sequential scan is cheaper
    int is_ok;
    char error[256];
} QueryPlanCostResult;

/**
 * Estimates the cost of a B-Tree index range scan vs sequential scan.
 * Implements PostgreSQL's cost model:
 *   index_scan_cost = tree_height * random_page_cost + selectivity * seq_page_cost
 *   seq_scan_cost = total_pages * seq_page_cost + total_rows * cpu_tuple_cost
 *
 * @param stats       Index statistics from pg_statistic / ANALYZE
 * @param range_low   Selectivity lower bound (0.0 to 1.0)
 * @param range_high  Selectivity upper bound (0.0 to 1.0)
 * @return QueryPlanCostResult with estimated costs and index vs seq recommendation
 */
QueryPlanCostResult omni_sql_btree_range_scan_cost(
    BTreeIndexStats stats,
    double range_low,
    double range_high
) {
    QueryPlanCostResult res;
    memset(&res, 0, sizeof(QueryPlanCostResult));
    res.is_ok = 0;

    if (stats.total_rows == 0) {
        strcpy(res.error, "SQL planner: table has zero rows — no cost estimation possible.");
        return res;
    }
    if (stats.distinct_values == 0 || stats.tree_height <= 0) {
        strcpy(res.error, "SQL planner: invalid index statistics (distinct=0 or height<=0).");
        return res;
    }
    if (range_low < 0.0 || range_high > 1.0 || range_low > range_high) {
        strcpy(res.error, "SQL planner: selectivity range must be [0.0, 1.0] and low <= high.");
        return res;
    }

    // PostgreSQL cost constants
    const double seq_page_cost = 1.0;
    const double random_page_cost = 4.0;
    const double cpu_tuple_cost = 0.01;
    const double cpu_index_tuple_cost = 0.005;

    // Compute selectivity and estimated matching rows
    double selectivity = range_high - range_low;
    res.estimated_rows = (double)stats.total_rows * selectivity;

    // Total pages in heap
    int rows_per_page = stats.page_size_bytes / stats.row_size_bytes;
    if (rows_per_page <= 0) rows_per_page = 1;
    double total_pages = ceil((double)stats.total_rows / rows_per_page);

    // === Index Scan Cost ===
    // Tree traversal: tree_height random I/O operations
    double index_io = stats.tree_height * random_page_cost;

    // Leaf pages to read: proportional to selectivity
    double index_leaf_pages = ceil(selectivity * total_pages);
    index_io += index_leaf_pages * random_page_cost;

    // Heap fetches: one random I/O per matching row (worst case)
    double heap_io = fmin(res.estimated_rows, total_pages) * random_page_cost;

    double index_cpu = res.estimated_rows * cpu_index_tuple_cost;

    double index_total_cost = index_io + heap_io + index_cpu;

    // === Sequential Scan Cost ===
    double seq_io = total_pages * seq_page_cost;
    double seq_cpu = (double)stats.total_rows * cpu_tuple_cost;
    double seq_total_cost = seq_io + seq_cpu;

    // Decision: use whichever is cheaper
    res.estimated_io_cost = index_io + heap_io;
    res.estimated_cpu_cost = index_cpu;
    res.total_cost = index_total_cost;
    res.use_index_scan = (index_total_cost < seq_total_cost) ? 1 : 0;

    res.is_ok = 1;
    return res;
}
