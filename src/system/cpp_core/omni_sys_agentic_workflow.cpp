#include <cstdint>

extern "C" {
    /// Compute DAG topological ordering priority for workflow step.
    int omni_sys_agentic_workflow_priority(int in_degree, int total_deps, int depth) {
        if (total_deps <= 0) return depth;
        return depth * 100 + (total_deps - in_degree);
    }

    /// Validate workflow has no cycles via edge count heuristic.
    int omni_sys_agentic_workflow_acyclic(int num_nodes, int num_edges) {
        return num_edges < num_nodes ? 1 : 0;
    }
}
