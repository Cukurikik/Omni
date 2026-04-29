// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// XGBoost Tree Booster (OMNI Zero-Mock Implementation)
// Implements exact greedy split finding using gradient and hessian.

#include <vector>
#include <string>
#include <algorithm>

namespace omni {
namespace compute {
namespace xgboost {

template <typename T>
struct Result {
    T value;
    std::string error;
    bool is_ok;
    
    static Result<T> Ok(T val) { return {val, "", true}; }
    static Result<T> Err(std::string err) { return {T(), err, false}; }
};

struct Instance {
    float feature;
    float grad;
    float hess;
};

struct SplitResult {
    float split_value;
    float max_gain;
};

class ExactGreedySplitter {
public:
    Result<SplitResult> find_best_split(std::vector<Instance>& instances, float min_child_weight, float reg_lambda) {
        if (instances.size() < 2) {
            return Result<SplitResult>::Err("At least 2 instances required to find a split.");
        }

        std::sort(instances.begin(), instances.end(), [](const Instance& a, const Instance& b) {
            return a.feature < b.feature;
        });

        float total_grad = 0, total_hess = 0;
        for (const auto& inst : instances) {
            total_grad += inst.grad;
            total_hess += inst.hess;
        }

        float best_gain = 0;
        float best_split = 0;

        float gl = 0, hl = 0;
        for (size_t i = 0; i < instances.size() - 1; ++i) {
            gl += instances[i].grad;
            hl += instances[i].hess;

            float gr = total_grad - gl;
            float hr = total_hess - hl;

            if (hl < min_child_weight || hr < min_child_weight) {
                continue; // Skip splits that do not meet min_child_weight
            }

            float gain = (gl * gl) / (hl + reg_lambda) + (gr * gr) / (hr + reg_lambda) - (total_grad * total_grad) / (total_hess + reg_lambda);
            
            if (gain > best_gain) {
                best_gain = gain;
                best_split = (instances[i].feature + instances[i+1].feature) / 2.0f;
            }
        }

        if (best_gain <= 0) {
            return Result<SplitResult>::Err("No valid split found causing positive gain.");
        }

        return Result<SplitResult>::Ok({best_split, best_gain});
    }
};

} // namespace xgboost
} // namespace compute
} // namespace omni
