#include <vector>
#include <cmath>
#include <string>
#include <cstring>

// FastEdit ROME (Rank-One Model Editing) Kernel
// Production implementation of rank-one weight update for FFN layers

template <typename T, typename E>
struct OmniResult {
    bool is_ok;
    T value;
    E error;
};

struct ROMEUpdate {
    uint32_t layer_idx;
    float* delta_weights;     // rank-one update: u * v^T
    uint32_t rows;
    uint32_t cols;
};

class ROMEKernel {
private:
    static constexpr uint32_t MAX_LAYERS = 128;
    static constexpr uint32_t MAX_HIDDEN_DIM = 16384;
    static constexpr uint32_t MAX_EDITS_PER_BATCH = 256;

public:
    // Compute rank-one update: delta_W = (v_new - v_old) * k^T / (k^T * C^{-1} * k)
    OmniResult<ROMEUpdate, std::string> compute_rank_one_update(
        const float* key_vector,
        const float* value_old,
        const float* value_new,
        const float* covariance_inv_diag,
        uint32_t hidden_dim,
        uint32_t layer_idx
    ) {
        if (hidden_dim > MAX_HIDDEN_DIM) {
            return {false, {}, "Hidden dimension exceeds hardware limit"};
        }
        if (layer_idx >= MAX_LAYERS) {
            return {false, {}, "Layer index out of bounds"};
        }

        // Compute denominator: k^T * C^{-1} * k (scalar)
        double denominator = 0.0;
        for (uint32_t i = 0; i < hidden_dim; ++i) {
            denominator += (double)key_vector[i] * covariance_inv_diag[i] * key_vector[i];
        }
        if (std::abs(denominator) < 1e-12) {
            return {false, {}, "Denominator near zero — numerical instability"};
        }

        // Compute value delta: v_new - v_old
        std::vector<float> v_delta(hidden_dim);
        for (uint32_t i = 0; i < hidden_dim; ++i) {
            v_delta[i] = value_new[i] - value_old[i];
        }

        // Compute normalized key: C^{-1} * k / (k^T * C^{-1} * k)
        std::vector<float> k_norm(hidden_dim);
        for (uint32_t i = 0; i < hidden_dim; ++i) {
            k_norm[i] = (float)(covariance_inv_diag[i] * key_vector[i] / denominator);
        }

        // Compute outer product: delta_W = v_delta * k_norm^T
        float* delta_w = new float[hidden_dim * hidden_dim];
        for (uint32_t i = 0; i < hidden_dim; ++i) {
            for (uint32_t j = 0; j < hidden_dim; ++j) {
                delta_w[i * hidden_dim + j] = v_delta[i] * k_norm[j];
            }
        }

        ROMEUpdate update{layer_idx, delta_w, hidden_dim, hidden_dim};
        return {true, update, ""};
    }

    // Apply the rank-one update to target weight matrix in-place
    OmniResult<bool, std::string> apply_update(
        float* weight_matrix,
        const ROMEUpdate& update
    ) {
        if (!weight_matrix || !update.delta_weights) {
            return {false, false, "Null pointer in weight application"};
        }
        uint32_t total = update.rows * update.cols;
        for (uint32_t i = 0; i < total; ++i) {
            weight_matrix[i] += update.delta_weights[i];
        }
        return {true, true, ""};
    }
};
