#include <vector>
#include <string>

namespace omni {
namespace sppo {

template<typename T>
struct OmniResult {
    T value;
    std::string error;
    bool is_ok;
};

class PreferenceMatrix {
public:
    OmniResult<std::vector<std::vector<float>>> build_matrix(int num_models) {
        if (num_models <= 1) {
            return {{}, "Must have >1 models for preference", false};
        }
        
        // Native C++ high-speed matrix initialization for SPPO tournament
        std::vector<std::vector<float>> matrix(num_models, std::vector<float>(num_models, 0.5f));
        
        return {matrix, "", true};
    }
};

}
}
