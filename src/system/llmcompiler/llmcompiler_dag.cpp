#include <vector>
#include <queue>
#include <mutex>
#include <unordered_map>

// LLMCompiler DAG Scheduler
// Manages dependency graphs for parallel function calling.

template <typename T, typename E>
struct OmniResult {
    bool is_ok;
    T value;
    E error;
};

struct DagNode {
    uint32_t id;
    std::vector<uint32_t> dependencies;
    bool completed;
};

class LLMCompilerDAG {
private:
    std::unordered_map<uint32_t, DagNode> nodes;
    std::mutex dag_mutex;
    const uint32_t MAX_NODES = 10000;

public:
    OmniResult<bool, std::string> add_node(uint32_t id, const std::vector<uint32_t>& deps) {
        std::lock_guard<std::mutex> lock(dag_mutex);
        if (nodes.size() >= MAX_NODES) {
            return {false, false, "Exceeded maximum DAG node limits"};
        }
        nodes[id] = {id, deps, false};
        return {true, true, ""};
    }

    OmniResult<std::vector<uint32_t>, std::string> get_executable_nodes() {
        std::lock_guard<std::mutex> lock(dag_mutex);
        std::vector<uint32_t> executable;
        
        for (const auto& [id, node] : nodes) {
            if (node.completed) continue;
            bool can_execute = true;
            for (uint32_t dep : node.dependencies) {
                if (nodes.find(dep) != nodes.end() && !nodes[dep].completed) {
                    can_execute = false;
                    break;
                }
            }
            if (can_execute) {
                executable.push_back(id);
            }
        }
        return {true, executable, ""};
    }

    OmniResult<bool, std::string> mark_completed(uint32_t id) {
        std::lock_guard<std::mutex> lock(dag_mutex);
        if (nodes.find(id) != nodes.end()) {
            nodes[id].completed = true;
            return {true, true, ""};
        }
        return {false, false, "Node not found"};
    }
};
