// Omni DuQuant Hadamard Rotation Kernel (C++)
// Ref: Hsu1023/DuQuant — NeurIPS'24 Oral | MIT
#include <vector>
#include <cmath>
#include <algorithm>
namespace omni { namespace duquant {
std::vector<float> hadamard_rotate(const std::vector<float>& x) {
    int n = x.size(); if (n == 0) return {};
    float factor = 1.0f / std::sqrt((float)n);
    std::vector<float> out(n, 0);
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j) {
            int sign = (__builtin_popcount(i & j) % 2 == 0) ? 1 : -1;
            out[i] += sign * x[j];
        }
    for (auto& v : out) v *= factor;
    return out;
}
int symmetric_quantize(float val, int n_bits) {
    int qmax = (1 << (n_bits - 1)) - 1;
    int q = static_cast<int>(std::round(val * qmax));
    return std::max(-qmax, std::min(qmax, q));
}
float outlier_ratio(const std::vector<float>& w, float thresh_std) {
    if (w.empty()) return 0;
    float sum = 0; for (auto v : w) sum += v; float mean = sum / w.size();
    float var = 0; for (auto v : w) var += (v-mean)*(v-mean); float std = std::sqrt(var / w.size());
    int out = 0; for (auto v : w) if (std::abs(v-mean) > thresh_std * std) out++;
    return (float)out / w.size();
}
}}
