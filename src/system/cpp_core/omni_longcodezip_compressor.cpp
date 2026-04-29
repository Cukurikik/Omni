// Omni LongCodeZip Token Compressor (C++)
// System Layer: High-perf token importance scoring for code compression.
// Ref: YerbaPage/LongCodeZip — ASE 2025

#include <cstddef>
#include <algorithm>
struct TokenScore { int index; float score; };
int rank_tokens(const float* scores, int n, TokenScore* out, int max_out) {
    int count = n < max_out ? n : max_out;
    for (int i = 0; i < count; ++i) out[i] = {i, scores[i]};
    std::sort(out, out + count, [](const TokenScore& a, const TokenScore& b){ return a.score > b.score; });
    return count;
}
