#include <cstdint>

extern "C" {
    /// Chunk text into fixed-size windows with overlap.
    int omni_sys_anything_llm_chunk_count(int text_len, int chunk_size, int overlap) {
        if (text_len <= 0 || chunk_size <= 0) return 0;
        if (chunk_size >= text_len) return 1;
        int step = chunk_size - overlap;
        if (step <= 0) step = 1;
        return (text_len - chunk_size) / step + 1;
    }

    /// Compute embedding cosine similarity from dot product and norms.
    float omni_sys_anything_llm_cosine_sim(float dot, float norm_a, float norm_b) {
        if (norm_a <= 0.0f || norm_b <= 0.0f) return 0.0f;
        return dot / (norm_a * norm_b);
    }
}
