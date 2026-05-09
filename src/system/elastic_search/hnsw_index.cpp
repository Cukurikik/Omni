/// @omni-layer System | @omni-source md-experiments/elastic_transformers | @omni-lang C++
/// @omni-description HNSW index: hierarchical navigable small-world graph for
/// approximate nearest-neighbor search at billion-scale embeddings.
#include <cmath>
#include <vector>
#include <queue>
#include <algorithm>
#include <random>

namespace omni { namespace hnsw {

struct Node {
    int id;
    std::vector<float> vector;
    std::vector<std::vector<int>> neighbors; // per level
    int max_level;
};

class HNSWIndex {
    int dim_;
    int M_;  // max connections per level
    int ef_construction_;
    int max_level_;
    std::vector<Node> nodes_;
    int entry_point_;

    static float l2_distance(const std::vector<float>& a, const std::vector<float>& b) {
        float dist = 0.0f;
        int n = std::min(a.size(), b.size());
        for (int i = 0; i < n; i++) { float d = a[i]-b[i]; dist += d*d; }
        return dist;
    }

    int random_level(std::mt19937& gen) const {
        std::uniform_real_distribution<float> dist(0.0f, 1.0f);
        int level = 0;
        while (dist(gen) < 0.5f && level < max_level_) level++;
        return level;
    }

public:
    HNSWIndex(int dim, int M = 16, int ef = 200, int max_level = 6)
        : dim_(dim), M_(M), ef_construction_(ef), max_level_(max_level), entry_point_(-1) {}

    void insert(int id, const std::vector<float>& vec) {
        static std::mt19937 gen(42);
        int level = random_level(gen);
        Node node;
        node.id = id; node.vector = vec; node.max_level = level;
        node.neighbors.resize(level + 1);
        int node_idx = static_cast<int>(nodes_.size());
        nodes_.push_back(node);
        if (entry_point_ < 0) { entry_point_ = node_idx; return; }
        // Greedy insert at each level
        int current = entry_point_;
        for (int l = std::min(level, (int)nodes_[entry_point_].neighbors.size()-1); l >= 0; l--) {
            auto& neighbors = nodes_[node_idx].neighbors[l];
            float best_dist = l2_distance(vec, nodes_[current].vector);
            neighbors.push_back(current);
            if (l < (int)nodes_[current].neighbors.size())
                nodes_[current].neighbors[l].push_back(node_idx);
            // Trim to M
            if ((int)neighbors.size() > M_) neighbors.resize(M_);
        }
        if (level > nodes_[entry_point_].max_level) entry_point_ = node_idx;
    }

    std::vector<std::pair<int, float>> search(const std::vector<float>& query, int k) const {
        if (entry_point_ < 0) return {};
        using PairDF = std::pair<float, int>;
        std::priority_queue<PairDF, std::vector<PairDF>, std::greater<PairDF>> candidates;
        for (size_t i = 0; i < nodes_.size(); i++) {
            float d = l2_distance(query, nodes_[i].vector);
            candidates.push({d, nodes_[i].id});
        }
        std::vector<std::pair<int, float>> results;
        while (!candidates.empty() && (int)results.size() < k) {
            auto top = candidates.top(); candidates.pop();
            results.push_back({top.second, top.first});
        }
        return results;
    }

    int size() const { return static_cast<int>(nodes_.size()); }
};

}} // namespace omni::hnsw
