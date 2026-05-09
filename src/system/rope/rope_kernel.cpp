// @omni-layer System | @omni-source facebookresearch/llama | @omni-lang C++
// @omni-description RoPE frequency computation kernel: precomputed rotation
// matrices for position encoding with extended context support.
#include <vector>
#include <cmath>
#include <variant>
#include <string>

struct RoPEError { std::string msg; };
template<typename T> using OmniResult = std::variant<T, RoPEError>;

struct RotaryFreqs {
    std::vector<std::pair<double,double>> cos_sin;
    int position;
};

class RoPEKernel {
    int d_head_;
    double base_;
    int max_seq_;
    std::vector<std::vector<std::pair<double,double>>> cache_;
public:
    RoPEKernel(int d_head, double base = 10000.0, int max_seq = 8192)
        : d_head_(d_head), base_(base), max_seq_(max_seq) {
        cache_.resize(max_seq);
        for (int pos = 0; pos < max_seq; ++pos) {
            cache_[pos].resize(d_head / 2);
            for (int i = 0; i < d_head / 2; ++i) {
                double theta = static_cast<double>(pos) / std::pow(base, 2.0 * i / d_head);
                cache_[pos][i] = {std::cos(theta), std::sin(theta)};
            }
        }
    }

    OmniResult<std::vector<double>> apply(const std::vector<double>& x, int position) const {
        if (position >= max_seq_) return RoPEError{"Position exceeds max"};
        auto result = x;
        const auto& freqs = cache_[position];
        for (size_t i = 0; i < freqs.size() && 2*i+1 < result.size(); ++i) {
            double x0 = result[2*i], x1 = result[2*i+1];
            result[2*i] = x0 * freqs[i].first - x1 * freqs[i].second;
            result[2*i+1] = x0 * freqs[i].second + x1 * freqs[i].first;
        }
        return result;
    }

    OmniResult<std::vector<std::vector<double>>> apply_batch(
        const std::vector<std::vector<double>>& vectors, int start_pos
    ) const {
        std::vector<std::vector<double>> out;
        for (size_t i = 0; i < vectors.size(); ++i) {
            auto r = apply(vectors[i], start_pos + static_cast<int>(i));
            if (auto* err = std::get_if<RoPEError>(&r)) return *err;
            out.push_back(std::get<std::vector<double>>(r));
        }
        return out;
    }
};
