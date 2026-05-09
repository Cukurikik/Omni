// @omni-layer System | @omni-source xmed-lab/TAM
// @omni-description Token activation map rasterizer in C++: GPU-ready heatmap generation
// from attention weights for MLLM explainability visualization.
// @omni-lang C++ | @omni-batch 16 | @omni-semester 16

#include <vector>
#include <cmath>
#include <algorithm>
#include <variant>
#include <string>

struct TAMError { std::string msg; };
template<typename T> using OmniResult = std::variant<T, TAMError>;

struct HeatmapResult {
    std::vector<std::vector<float>> heatmap;
    int grid_size;
    float max_activation;
    float mean_activation;
};

class TokenActivationRasterizer {
    int grid_size_;
    int patch_size_;
    int image_size_;
public:
    TokenActivationRasterizer(int image_size, int patch_size)
        : image_size_(image_size), patch_size_(patch_size),
          grid_size_(image_size / patch_size) {}

    OmniResult<HeatmapResult> rasterize(const std::vector<float>& relevance) const {
        if (relevance.empty()) return TAMError{"Empty relevance"};
        int gs = grid_size_;
        HeatmapResult result;
        result.grid_size = gs;
        result.heatmap.resize(gs, std::vector<float>(gs, 0.0f));
        float max_val = 0.0f, sum_val = 0.0f;
        int count = std::min(static_cast<int>(relevance.size()), gs * gs);
        for (int i = 0; i < count; ++i) {
            int r = i / gs, c = i % gs;
            float v = std::max(0.0f, relevance[i]);
            result.heatmap[r][c] = v;
            max_val = std::max(max_val, v);
            sum_val += v;
        }
        if (max_val > 0) {
            for (auto& row : result.heatmap)
                for (auto& v : row) v /= max_val;
        }
        result.max_activation = max_val;
        result.mean_activation = count > 0 ? sum_val / count : 0.0f;
        return result;
    }

    OmniResult<std::vector<std::vector<float>>> bilinear_upscale(
        const std::vector<std::vector<float>>& heatmap, int target_size
    ) const {
        if (heatmap.empty()) return TAMError{"Empty heatmap"};
        int src = static_cast<int>(heatmap.size());
        std::vector<std::vector<float>> upscaled(target_size, std::vector<float>(target_size));
        float scale = static_cast<float>(src) / target_size;
        for (int i = 0; i < target_size; ++i) {
            for (int j = 0; j < target_size; ++j) {
                float src_r = i * scale, src_c = j * scale;
                int r0 = std::min(static_cast<int>(src_r), src - 1);
                int c0 = std::min(static_cast<int>(src_c), src - 1);
                upscaled[i][j] = heatmap[r0][c0];
            }
        }
        return upscaled;
    }
};
