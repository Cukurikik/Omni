// moe_dead_code_eliminator.cpp — System / Compiler
// Layer: System / Optimization — Dead Code Elimination
//
// During the PyTorch JIT to ONNX conversion, intermediate calculation nodes 
// (e.g. asserts, unused attention masks) often pollute the computation graph.
// This C++ module acts as a custom compiler pass to traverse the AST and prune
// dead nodes before handing the model over to TensorRT.

#include <iostream>
#include <vector>
#include <string>
#include <unordered_set>
#include <unordered_map>

namespace omni {
namespace moe {
namespace compiler {

struct GraphNode {
    int id;
    std::string op_type;
    std::vector<int> inputs;
    std::vector<int> outputs;
};

class DeadCodeEliminator {
private:
    std::unordered_map<int, GraphNode> nodes;
    int root_node_id;

public:
    DeadCodeEliminator(int root_id) : root_node_id(root_id) {
        std::cout << "[Compiler Pass] Initialized Dead Code Eliminator for Graph IR." << std::endl;
    }

    void add_node(int id, std::string op, std::vector<int> in, std::vector<int> out) {
        nodes[id] = GraphNode{id, op, in, out};
    }

    /**
     * @brief Performs a reverse topological search from the root output node
     * to identify which nodes actually contribute to the final result.
     */
    void run_pass() {
        std::unordered_set<int> reachable_nodes;
        std::vector<int> stack;
        
        // Start from the final output node
        stack.push_back(root_node_id);
        
        while (!stack.empty()) {
            int current = stack.back();
            stack.pop_back();
            
            if (reachable_nodes.find(current) == reachable_nodes.end()) {
                reachable_nodes.insert(current);
                
                // Add all inputs of this node to the stack
                if (nodes.find(current) != nodes.end()) {
                    for (int input_id : nodes[current].inputs) {
                        stack.push_back(input_id);
                    }
                }
            }
        }

        // Remove unreachable nodes
        int pruned_count = 0;
        for (auto it = nodes.begin(); it != nodes.end(); ) {
            if (reachable_nodes.find(it->first) == reachable_nodes.end()) {
                it = nodes.erase(it);
                pruned_count++;
            } else {
                ++it;
            }
        }
        
        std::cout << "[Compiler Pass] Dead Code Elimination Complete. Pruned " << pruned_count << " orphaned nodes." << std::endl;
    }
};

} // namespace compiler
} // namespace moe
} // namespace omni
