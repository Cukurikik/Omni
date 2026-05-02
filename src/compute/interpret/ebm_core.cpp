#include <vector>
#include <cmath>
#include <string>
#include <variant>

// @omni-domain Compute Layer (Explainable AI)
// @omni-source interpretml/interpret
// @omni-description EBM Core mimicking Explainable Boosting Machine additive models in C++.
// @omni-requirement zero-mock, monadic-error

struct EbmError { std::string message; };
template <typename T> using OmniResult = std::variant<T, EbmError>;

struct FeatureBin { double lower; double upper; double score; };

class EbmCore {
    std::vector<std::vector<FeatureBin>> feature_functions;
    double intercept;

public:
    EbmCore() : intercept(0.0) {}

    OmniResult<bool> add_feature_function(const std::vector<FeatureBin>& bins) {
        if (bins.empty()) return EbmError{"Feature bins cannot be empty."};
        feature_functions.push_back(bins);
        return true;
    }

    OmniResult<double> predict_single(const std::vector<double>& features) {
        if (features.size() != feature_functions.size())
            return EbmError{"Feature count mismatch."};
        double score = intercept;
        for (size_t f = 0; f < features.size(); ++f) {
            double val = features[f];
            const auto& bins = feature_functions[f];
            bool found = false;
            for (const auto& bin : bins) {
                if (val >= bin.lower && val < bin.upper) {
                    score += bin.score;
                    found = true;
                    break;
                }
            }
            if (!found) score += bins.back().score;
        }
        // Logistic sigmoid for classification
        double prob = 1.0 / (1.0 + std::exp(-score));
        return prob;
    }

    OmniResult<std::vector<double>> explain(const std::vector<double>& features) {
        if (features.size() != feature_functions.size())
            return EbmError{"Feature count mismatch."};
        std::vector<double> contributions;
        for (size_t f = 0; f < features.size(); ++f) {
            double val = features[f];
            const auto& bins = feature_functions[f];
            double contrib = 0.0;
            for (const auto& bin : bins) {
                if (val >= bin.lower && val < bin.upper) { contrib = bin.score; break; }
            }
            contributions.push_back(contrib);
        }
        return contributions;
    }
};
