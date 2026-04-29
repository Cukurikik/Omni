#include <vector>
#include <string>

namespace omni {
namespace system {

template<typename T>
struct OmniResult {
    T value;
    std::string error;
    bool is_ok;
};

class SpladeIndexer {
public:
    OmniResult<std::vector<int>> build_inverted_index(const std::vector<float>& sparse_vector, float threshold) {
        if (sparse_vector.empty() || threshold < 0.0f) {
            return {{}, "Invalid sparse vector or threshold", false};
        }
        
        std::vector<int> active_tokens;
        // Native C++ iteration for SPLADE sparse embedding indexing
        for (size_t i = 0; i < sparse_vector.size(); ++i) {
            if (sparse_vector[i] > threshold) {
                active_tokens.push_back(static_cast<int>(i));
            }
        }
        
        return {active_tokens, "", true};
    }
};

}
}
