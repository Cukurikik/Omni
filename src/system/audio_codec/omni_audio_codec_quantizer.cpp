// omni_audio_codec_quantizer.cpp — Residual Vector Quantization Engine
// Inspired by: SoundStorm + RQ-Transformer neural audio codec
// Layer: System / C++ Compute
//
// Production C++ implementation of cascading residual vector quantization
// for neural audio codecs (SoundStream, EnCodec style).

#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <cstring>
#include <cassert>
#include <memory>
#include <random>
#include <limits>

namespace omni {
namespace audio {

struct Codebook {
    std::vector<float> entries;  // (num_entries * dim)
    int num_entries;
    int dim;

    Codebook() : num_entries(0), dim(0) {}

    Codebook(int n, int d) : num_entries(n), dim(d), entries(n * d, 0.0f) {}

    const float* entry(int idx) const {
        assert(idx >= 0 && idx < num_entries);
        return entries.data() + idx * dim;
    }

    float* entry_mut(int idx) {
        assert(idx >= 0 && idx < num_entries);
        return entries.data() + idx * dim;
    }

    // Squared L2 distance between query and codebook entry
    float distance(const float* query, int idx) const {
        const float* e = entry(idx);
        float dist = 0.0f;
        for (int d = 0; d < dim; d++) {
            float diff = query[d] - e[d];
            dist += diff * diff;
        }
        return dist;
    }

    // Find nearest neighbor in codebook
    int nearest(const float* query) const {
        int best_idx = 0;
        float best_dist = std::numeric_limits<float>::max();
        for (int i = 0; i < num_entries; i++) {
            float d = distance(query, i);
            if (d < best_dist) {
                best_dist = d;
                best_idx = i;
            }
        }
        return best_idx;
    }

    // Initialize codebook entries from data using K-means++
    void initialize_kmeanspp(const float* data, int num_samples, std::mt19937& rng) {
        assert(num_samples >= num_entries);

        // First center: random sample
        std::uniform_int_distribution<int> dist(0, num_samples - 1);
        int first = dist(rng);
        std::memcpy(entry_mut(0), data + first * dim, dim * sizeof(float));

        std::vector<float> min_dists(num_samples, std::numeric_limits<float>::max());

        for (int c = 1; c < num_entries; c++) {
            // Update minimum distances
            for (int s = 0; s < num_samples; s++) {
                float d = distance(data + s * dim, c - 1);
                min_dists[s] = std::min(min_dists[s], d);
            }

            // Weighted sampling proportional to squared distance
            float total = std::accumulate(min_dists.begin(), min_dists.end(), 0.0f);
            std::uniform_real_distribution<float> udist(0.0f, total);
            float target = udist(rng);
            float cumulative = 0.0f;
            int selected = num_samples - 1;
            for (int s = 0; s < num_samples; s++) {
                cumulative += min_dists[s];
                if (cumulative >= target) {
                    selected = s;
                    break;
                }
            }
            std::memcpy(entry_mut(c), data + selected * dim, dim * sizeof(float));
        }
    }
};

// Configuration for residual quantization
struct RVQConfig {
    int num_levels;       // number of quantization levels (codebook cascade)
    int codebook_size;    // entries per codebook
    int dim;              // feature dimension
    int kmeans_iters;     // K-means iterations for codebook training

    RVQConfig() : num_levels(8), codebook_size(1024), dim(128), kmeans_iters(50) {}
};

// Residual Vector Quantizer
class ResidualVectorQuantizer {
public:
    explicit ResidualVectorQuantizer(const RVQConfig& config)
        : config_(config)
    {
        codebooks_.reserve(config.num_levels);
        for (int level = 0; level < config.num_levels; level++) {
            codebooks_.emplace_back(config.codebook_size, config.dim);
        }
    }

    // Encode a single vector into multi-level codes
    std::vector<int> encode(const float* input) const {
        std::vector<int> codes(config_.num_levels);
        std::vector<float> residual(config_.dim);
        std::memcpy(residual.data(), input, config_.dim * sizeof(float));

        for (int level = 0; level < config_.num_levels; level++) {
            int code = codebooks_[level].nearest(residual.data());
            codes[level] = code;

            // Compute residual: r = r - codebook[code]
            const float* entry = codebooks_[level].entry(code);
            for (int d = 0; d < config_.dim; d++) {
                residual[d] -= entry[d];
            }
        }
        return codes;
    }

    // Decode multi-level codes back to a vector
    std::vector<float> decode(const std::vector<int>& codes) const {
        assert(static_cast<int>(codes.size()) == config_.num_levels);
        std::vector<float> output(config_.dim, 0.0f);

        for (int level = 0; level < config_.num_levels; level++) {
            const float* entry = codebooks_[level].entry(codes[level]);
            for (int d = 0; d < config_.dim; d++) {
                output[d] += entry[d];
            }
        }
        return output;
    }

    // Encode a batch of vectors
    std::vector<std::vector<int>> encode_batch(
        const float* data, int num_samples
    ) const {
        std::vector<std::vector<int>> all_codes(num_samples);
        for (int s = 0; s < num_samples; s++) {
            all_codes[s] = encode(data + s * config_.dim);
        }
        return all_codes;
    }

    // Decode a batch of codes
    std::vector<float> decode_batch(
        const std::vector<std::vector<int>>& all_codes
    ) const {
        int num_samples = static_cast<int>(all_codes.size());
        std::vector<float> output(num_samples * config_.dim, 0.0f);
        for (int s = 0; s < num_samples; s++) {
            auto decoded = decode(all_codes[s]);
            std::memcpy(output.data() + s * config_.dim,
                        decoded.data(), config_.dim * sizeof(float));
        }
        return output;
    }

    // Train codebooks on data using iterative K-means
    void train(const float* data, int num_samples, uint32_t seed = 42) {
        std::mt19937 rng(seed);
        std::vector<float> residuals(num_samples * config_.dim);
        std::memcpy(residuals.data(), data, num_samples * config_.dim * sizeof(float));

        for (int level = 0; level < config_.num_levels; level++) {
            // Initialize codebook with K-means++
            codebooks_[level].initialize_kmeanspp(residuals.data(), num_samples, rng);

            // Run K-means iterations
            std::vector<int> assignments(num_samples);
            std::vector<int> counts(config_.codebook_size);

            for (int iter = 0; iter < config_.kmeans_iters; iter++) {
                // Assignment step
                for (int s = 0; s < num_samples; s++) {
                    assignments[s] = codebooks_[level].nearest(
                        residuals.data() + s * config_.dim
                    );
                }

                // Update step
                std::fill(counts.begin(), counts.end(), 0);
                std::vector<float> sums(config_.codebook_size * config_.dim, 0.0f);

                for (int s = 0; s < num_samples; s++) {
                    int c = assignments[s];
                    counts[c]++;
                    for (int d = 0; d < config_.dim; d++) {
                        sums[c * config_.dim + d] += residuals[s * config_.dim + d];
                    }
                }

                for (int c = 0; c < config_.codebook_size; c++) {
                    if (counts[c] > 0) {
                        float inv = 1.0f / static_cast<float>(counts[c]);
                        for (int d = 0; d < config_.dim; d++) {
                            codebooks_[level].entry_mut(c)[d] =
                                sums[c * config_.dim + d] * inv;
                        }
                    }
                }
            }

            // Compute residuals for next level
            for (int s = 0; s < num_samples; s++) {
                int code = codebooks_[level].nearest(
                    residuals.data() + s * config_.dim
                );
                const float* entry = codebooks_[level].entry(code);
                for (int d = 0; d < config_.dim; d++) {
                    residuals[s * config_.dim + d] -= entry[d];
                }
            }
        }
    }

    // Compute reconstruction error (MSE)
    float compute_mse(const float* data, int num_samples) const {
        float total_error = 0.0f;
        for (int s = 0; s < num_samples; s++) {
            auto codes = encode(data + s * config_.dim);
            auto decoded = decode(codes);
            for (int d = 0; d < config_.dim; d++) {
                float diff = data[s * config_.dim + d] - decoded[d];
                total_error += diff * diff;
            }
        }
        return total_error / static_cast<float>(num_samples * config_.dim);
    }

    const RVQConfig& config() const { return config_; }
    int num_levels() const { return config_.num_levels; }
    int codebook_size() const { return config_.codebook_size; }

private:
    RVQConfig config_;
    std::vector<Codebook> codebooks_;
};

}  // namespace audio
}  // namespace omni
