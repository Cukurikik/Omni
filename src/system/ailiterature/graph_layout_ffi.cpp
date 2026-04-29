// OMNI SYSTEM LAYER: AI Literature (C++)
// FFI for high-speed Force-Directed Graph Layout (Fruchterman-Reingold).

#include <vector>
#include <cmath>

extern "C" {

    struct Node2D {
        double x, y;
        double dx, dy;
    };

    struct Edge {
        int source;
        int target;
    };

    // Computes layout directly in memory. Caller must free nodes if allocated outside.
    int omni_compute_force_layout(Node2D* nodes, int num_nodes, const Edge* edges, int num_edges, int iterations, double width, double height) {
        if (!nodes || !edges || num_nodes <= 0) return -1;

        double area = width * height;
        double k = std::sqrt(area / num_nodes);
        
        for (int iter = 0; iter < iterations; ++iter) {
            double temp = width / 10.0 * (1.0 - (double)iter / iterations);

            // Repulsive forces
            for (int i = 0; i < num_nodes; ++i) {
                nodes[i].dx = 0;
                nodes[i].dy = 0;
                for (int j = 0; j < num_nodes; ++j) {
                    if (i == j) continue;
                    double delta_x = nodes[i].x - nodes[j].x;
                    double delta_y = nodes[i].y - nodes[j].y;
                    double dist = std::sqrt(delta_x * delta_x + delta_y * delta_y) + 0.0001;
                    
                    double force = (k * k) / dist;
                    nodes[i].dx += (delta_x / dist) * force;
                    nodes[i].dy += (delta_y / dist) * force;
                }
            }

            // Attractive forces
            for (int e = 0; e < num_edges; ++e) {
                int u = edges[e].source;
                int v = edges[e].target;
                
                double delta_x = nodes[u].x - nodes[v].x;
                double delta_y = nodes[u].y - nodes[v].y;
                double dist = std::sqrt(delta_x * delta_x + delta_y * delta_y) + 0.0001;

                double force = (dist * dist) / k;
                double dx = (delta_x / dist) * force;
                double dy = (delta_y / dist) * force;

                nodes[u].dx -= dx;
                nodes[u].dy -= dy;
                nodes[v].dx += dx;
                nodes[v].dy += dy;
            }

            // Apply displacement
            for (int i = 0; i < num_nodes; ++i) {
                double dist = std::sqrt(nodes[i].dx * nodes[i].dx + nodes[i].dy * nodes[i].dy) + 0.0001;
                nodes[i].x += (nodes[i].dx / dist) * std::min(dist, temp);
                nodes[i].y += (nodes[i].dy / dist) * std::min(dist, temp);
                
                // Bounds check
                nodes[i].x = std::min(width, std::max(0.0, nodes[i].x));
                nodes[i].y = std::min(height, std::max(0.0, nodes[i].y));
            }
        }
        
        return 0; // Success
    }
}
