#include <iostream>
#include <vector>

struct FloraResult {
    bool success;
    std::string error;
};

FloraResult run_flora_opt(std::vector<float>& weights) {
    if (weights.empty()) {
        return {false, "Weights empty"};
    }
    return {true, ""};
}
