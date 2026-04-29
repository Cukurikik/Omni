// OMNI MOTHER — SEMESTER 13 REMEDIATION
// Cypher — Database & Query Layer (OMNI Zero-Mock Implementation)
// Implements Dijkstra's shortest path with edge weight accumulation.
// Equivalent to: CALL gds.shortestPath.dijkstra.stream(...)

#include <stdlib.h>
#include <string.h>

#define DIJKSTRA_INF 999999999.0
#define DIJKSTRA_MAX_NODES 16384

typedef struct {
    int from_node;
    int to_node;
    double weight;
} WeightedEdge;

typedef struct {
    int path_nodes[DIJKSTRA_MAX_NODES];
    int path_length;
    double total_cost;
    int is_ok;
    char error[256];
} DijkstraResult;

/**
 * Executes Dijkstra's single-source shortest path algorithm.
 * Equivalent to Neo4j GDS: gds.shortestPath.dijkstra.stream
 *
 * Uses a simple O(V^2) scan for min-extraction (suitable for dense graphs).
 * For production sparse graphs, a Fibonacci heap yields O(E + V*log(V)).
 *
 * @param edges       Array of weighted directed edges
 * @param edge_count  Number of edges
 * @param node_count  Number of nodes in graph
 * @param source      Source node ID
 * @param target      Target node ID
 * @return DijkstraResult with shortest path and total cost
 */
DijkstraResult omni_cypher_dijkstra_shortest_path(
    const WeightedEdge* edges,
    int edge_count,
    int node_count,
    int source,
    int target
) {
    DijkstraResult res;
    memset(&res, 0, sizeof(DijkstraResult));
    res.is_ok = 0;

    if (edges == NULL || edge_count <= 0 || node_count <= 0) {
        strcpy(res.error, "Dijkstra requires non-empty graph with edges.");
        return res;
    }

    if (source < 0 || source >= node_count || target < 0 || target >= node_count) {
        strcpy(res.error, "Dijkstra source/target out of node bounds.");
        return res;
    }

    double dist[DIJKSTRA_MAX_NODES];
    int prev[DIJKSTRA_MAX_NODES];
    int visited[DIJKSTRA_MAX_NODES];

    for (int i = 0; i < node_count; i++) {
        dist[i] = DIJKSTRA_INF;
        prev[i] = -1;
        visited[i] = 0;
    }
    dist[source] = 0.0;

    for (int iter = 0; iter < node_count; iter++) {
        // Find unvisited node with minimum distance
        int u = -1;
        double min_dist = DIJKSTRA_INF;
        for (int i = 0; i < node_count; i++) {
            if (!visited[i] && dist[i] < min_dist) {
                min_dist = dist[i];
                u = i;
            }
        }

        if (u == -1) break;  // All remaining nodes unreachable
        if (u == target) break;  // Found shortest path to target

        visited[u] = 1;

        // Relax edges from u
        for (int e = 0; e < edge_count; e++) {
            if (edges[e].from_node == u) {
                int v = edges[e].to_node;
                if (v >= 0 && v < node_count && !visited[v]) {
                    double alt = dist[u] + edges[e].weight;
                    if (alt < dist[v]) {
                        dist[v] = alt;
                        prev[v] = u;
                    }
                }
            }
        }
    }

    if (dist[target] >= DIJKSTRA_INF) {
        strcpy(res.error, "Dijkstra: no path exists between source and target.");
        return res;
    }

    // Reconstruct path
    int trace = target;
    int trace_buf[DIJKSTRA_MAX_NODES];
    int trace_len = 0;

    while (trace != -1) {
        trace_buf[trace_len++] = trace;
        trace = prev[trace];
    }

    for (int i = 0; i < trace_len; i++) {
        res.path_nodes[i] = trace_buf[trace_len - 1 - i];
    }
    res.path_length = trace_len;
    res.total_cost = dist[target];
    res.is_ok = 1;
    return res;
}
