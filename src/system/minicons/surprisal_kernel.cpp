// @omni-layer System | @omni-source kanishkamisra/minicons
// @omni-description Surprisal computation kernel in C++: vectorized log-softmax and
// token-level information content measurement.
// @omni-lang C++ | @omni-batch 16 | @omni-semester 16

#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <variant>
#include <string>

struct SurprisalError { std::string message; };
template<typename T> using OmniResult = std::variant<T, SurprisalError>;

struct SurprisalOutput {
    std::vector<double> surprisals_bits;
    double mean_surprisal;
    double entropy;
    size_t n_tokens;
};

class SurprisalKernel {
    size_t vocab_size_;
public:
    explicit SurprisalKernel(size_t vocab_size) : vocab_size_(vocab_size) {}

    std::vector<double> log_softmax(const std::vector<double>& logits) const {
        double max_val = *std::max_element(logits.begin(), logits.end());
        double log_sum = 0.0;
        for (auto l : logits) log_sum += std::exp(l - max_val);
        log_sum = std::log(log_sum);
        std::vector<double> result(logits.size());
        for (size_t i = 0; i < logits.size(); ++i)
            result[i] = logits[i] - max_val - log_sum;
        return result;
    }

    OmniResult<SurprisalOutput> compute_surprisal(
        const std::vector<std::vector<double>>& logits_seq,
        const std::vector<int>& token_ids
    ) const {
        if (logits_seq.size() != token_ids.size())
            return SurprisalError{"Logits/tokens size mismatch"};
        if (token_ids.empty())
            return SurprisalError{"Empty token sequence"};

        SurprisalOutput output;
        output.n_tokens = token_ids.size();
        output.surprisals_bits.resize(output.n_tokens);
        double total_entropy = 0.0;

        for (size_t i = 0; i < output.n_tokens; ++i) {
            auto log_probs = log_softmax(logits_seq[i]);
            int tid = token_ids[i] % static_cast<int>(log_probs.size());
            output.surprisals_bits[i] = -log_probs[tid] / std::log(2.0);
            for (auto lp : log_probs) total_entropy -= std::exp(lp) * lp;
        }
        output.mean_surprisal = std::accumulate(output.surprisals_bits.begin(),
            output.surprisals_bits.end(), 0.0) / output.n_tokens;
        output.entropy = total_entropy / output.n_tokens;
        return output;
    }

    OmniResult<double> perplexity(const std::vector<std::vector<double>>& logits,
                                   const std::vector<int>& tokens) const {
        auto result = compute_surprisal(logits, tokens);
        if (auto* err = std::get_if<SurprisalError>(&result)) return *err;
        auto& out = std::get<SurprisalOutput>(result);
        return std::pow(2.0, out.mean_surprisal);
    }
};
