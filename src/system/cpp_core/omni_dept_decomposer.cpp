// Omni DePT Prompt Matrix Decomposer (C++)
// Ref: ShiZhengyan/DePT — ICLR 2024
#include <vector>
#include <cmath>
struct DePTComponents { std::vector<float> shared; std::vector<float> task_specific; };
DePTComponents omni_decompose(const float* prompt, int dim, int rank) {
    DePTComponents c;
    c.shared.assign(prompt, prompt + rank);
    c.task_specific.assign(prompt + rank, prompt + dim);
    return c;
}
void omni_compose(const DePTComponents& c, float alpha, float* out, int dim) {
    int rank = (int)c.shared.size();
    for (int i = 0; i < rank; i++) out[i] = c.shared[i] * alpha;
    for (int i = 0; i < (int)c.task_specific.size(); i++) out[rank + i] = c.task_specific[i] * (1.0f - alpha);
}
float omni_orth_penalty(const float* shared, const float* task, int n) {
    float dot = 0;
    for (int i = 0; i < n; i++) dot += shared[i] * task[i];
    return fabsf(dot);
}
