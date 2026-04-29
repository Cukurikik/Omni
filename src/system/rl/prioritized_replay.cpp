#include <vector>

namespace Omni {
namespace RL {

class SumTree {
    std::vector<double> tree;
    size_t capacity;
public:
    SumTree(size_t cap) : capacity(cap) {
        tree.resize(2 * cap - 1, 0.0);
    }

    void add(size_t idx, double priority) {
        if (idx >= capacity) return;
        size_t tree_idx = idx + capacity - 1;
        double change = priority - tree[tree_idx];
        tree[tree_idx] = priority;
        while (tree_idx != 0) {
            tree_idx = (tree_idx - 1) / 2;
            tree[tree_idx] += change;
        }
    }
};

}} // namespace
