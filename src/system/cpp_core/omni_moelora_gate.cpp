// Omni MOELoRA Gate Kernel (C++)
// Ref: liuqidong07/MOELoRA-peft — SIGIR'24
#include <vector>
#include <cmath>
#include <algorithm>
namespace omni { namespace moelora {
std::vector<float> softmax_gate(const std::vector<float>& logits) {
    float mx = *std::max_element(logits.begin(), logits.end());
    std::vector<float> out(logits.size());
    float sum = 0;
    for (size_t i = 0; i < logits.size(); ++i) { out[i] = std::exp(logits[i]-mx); sum += out[i]; }
    for (auto& o : out) o /= sum;
    return out;
}
float load_balance_loss(const std::vector<std::vector<float>>& gates, int n_experts) {
    int B = gates.size(); if (!B) return 0;
    std::vector<float> avg(n_experts, 0), freq(n_experts, 0);
    for (auto& g : gates) {
        int top = std::max_element(g.begin(), g.end()) - g.begin();
        freq[top] += 1.0f / B;
        for (int e = 0; e < n_experts; ++e) avg[e] += g[e] / B;
    }
    float loss = 0;
    for (int e = 0; e < n_experts; ++e) loss += avg[e] * freq[e];
    return n_experts * loss;
}
}}
