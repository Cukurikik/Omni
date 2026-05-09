// moe_ring_attention.cpp — Ring Attention for MoE Long-Context
// Layer: System / GPU — MoE Long Context Processing
//
// Host-side implementation of ring attention adapted for MoE models.
// Distributes attention computation in a ring topology across devices,
// enabling sequence lengths far beyond single-device memory limits.

#include <cstdint>
#include <cstdlib>
#include <cmath>
#include <algorithm>
#include <vector>
#include <numeric>
#include <string>

namespace omni {
namespace moe {

struct RingAttentionConfig {
    int num_heads = 12;
    int head_dim = 64;
    int ring_size = 4;       // number of devices in ring
    int chunk_size = 1024;   // tokens per chunk
    int max_seq_len = 65536;
    float scale = 0.0f;     // 0 = auto (1/sqrt(head_dim))
    bool causal = true;
};

/// Chunk metadata for ring communication.
struct ChunkDescriptor {
    int rank;          // device rank in ring
    int chunk_id;      // chunk index within sequence
    int start_pos;     // start position in full sequence
    int end_pos;       // end position in full sequence
    int num_tokens;    // number of tokens in this chunk
};

/// Plan ring attention chunks.
std::vector<ChunkDescriptor> plan_ring_chunks(
    int seq_len,
    const RingAttentionConfig& config
) {
    int num_chunks = (seq_len + config.chunk_size - 1) / config.chunk_size;
    std::vector<ChunkDescriptor> chunks(num_chunks);

    for (int i = 0; i < num_chunks; ++i) {
        int start = i * config.chunk_size;
        int end = std::min(start + config.chunk_size, seq_len);
        chunks[i] = {
            .rank = i % config.ring_size,
            .chunk_id = i,
            .start_pos = start,
            .end_pos = end,
            .num_tokens = end - start,
        };
    }
    return chunks;
}

/// Compute the ring communication schedule.
/// Returns pairs of (send_to, recv_from) for each step.
struct CommStep {
    int send_to;
    int recv_from;
};

std::vector<std::vector<CommStep>> ring_schedule(int ring_size) {
    // Each device sends KV to the next and receives from previous
    // for ring_size - 1 steps (plus the initial local step)
    std::vector<std::vector<CommStep>> schedule(ring_size);

    for (int step = 0; step < ring_size; ++step) {
        schedule[step].resize(ring_size);
        for (int rank = 0; rank < ring_size; ++rank) {
            schedule[step][rank] = {
                .send_to = (rank + 1) % ring_size,
                .recv_from = (rank - 1 + ring_size) % ring_size,
            };
        }
    }
    return schedule;
}

/// Compute causal mask for ring attention.
/// Returns true if position q_pos can attend to kv_pos.
inline bool causal_mask(int q_pos, int kv_pos) {
    return kv_pos <= q_pos;
}

/// Compute attention scale factor.
inline float compute_scale(const RingAttentionConfig& config) {
    if (config.scale > 0) return config.scale;
    return 1.0f / std::sqrt(static_cast<float>(config.head_dim));
}

/// Compute softmax statistics for online (streaming) softmax.
struct SoftmaxState {
    float max_val = -1e30f;
    float sum_exp = 0.0f;

    void update(float new_max, float new_sum) {
        if (new_max > max_val) {
            float factor = std::exp(max_val - new_max);
            sum_exp = sum_exp * factor + new_sum;
            max_val = new_max;
        } else {
            float factor = std::exp(new_max - max_val);
            sum_exp += new_sum * factor;
        }
    }
};

/// Compute attention between a query chunk and a KV chunk.
/// Returns per-head partial attention output and softmax stats.
struct PartialAttentionOutput {
    std::vector<float> weighted_values;  // (num_q, head_dim)
    std::vector<SoftmaxState> softmax_states;  // (num_q,)
    int num_q;
    int head_dim;
};

PartialAttentionOutput compute_partial_attention(
    const float* queries,    // (num_q, head_dim)
    const float* keys,       // (num_kv, head_dim)
    const float* values,     // (num_kv, head_dim)
    int num_q,
    int num_kv,
    int head_dim,
    int q_offset,            // global position offset for queries
    int kv_offset,           // global position offset for KV
    bool causal,
    float scale
) {
    PartialAttentionOutput out;
    out.num_q = num_q;
    out.head_dim = head_dim;
    out.weighted_values.resize(num_q * head_dim, 0.0f);
    out.softmax_states.resize(num_q);

    for (int q = 0; q < num_q; ++q) {
        float local_max = -1e30f;
        float local_sum = 0.0f;

        // Compute attention scores for this query
        std::vector<float> scores(num_kv);
        const float* q_ptr = queries + q * head_dim;

        for (int kv = 0; kv < num_kv; ++kv) {
            if (causal && !causal_mask(q_offset + q, kv_offset + kv)) {
                scores[kv] = -1e30f;
                continue;
            }

            const float* k_ptr = keys + kv * head_dim;
            float dot = 0.0f;
            for (int d = 0; d < head_dim; ++d) {
                dot += q_ptr[d] * k_ptr[d];
            }
            scores[kv] = dot * scale;
            local_max = std::max(local_max, scores[kv]);
        }

        // Compute weighted values using online softmax
        for (int kv = 0; kv < num_kv; ++kv) {
            float w = std::exp(scores[kv] - local_max);
            local_sum += w;
            const float* v_ptr = values + kv * head_dim;
            for (int d = 0; d < head_dim; ++d) {
                out.weighted_values[q * head_dim + d] += w * v_ptr[d];
            }
        }

        out.softmax_states[q].update(local_max, local_sum);
    }

    return out;
}

/// Merge partial attention outputs using streaming softmax correction.
void merge_partial_outputs(
    PartialAttentionOutput& accumulated,
    const PartialAttentionOutput& incoming
) {
    for (int q = 0; q < accumulated.num_q; ++q) {
        auto& acc_state = accumulated.softmax_states[q];
        const auto& new_state = incoming.softmax_states[q];

        float old_max = acc_state.max_val;
        float new_max = std::max(old_max, new_state.max_val);

        float old_factor = std::exp(old_max - new_max);
        float new_factor = std::exp(new_state.max_val - new_max);

        float new_sum = acc_state.sum_exp * old_factor + new_state.sum_exp * new_factor;

        // Rescale accumulated values
        int offset = q * accumulated.head_dim;
        for (int d = 0; d < accumulated.head_dim; ++d) {
            accumulated.weighted_values[offset + d] =
                accumulated.weighted_values[offset + d] * old_factor +
                incoming.weighted_values[offset + d] * new_factor;
        }

        acc_state.max_val = new_max;
        acc_state.sum_exp = new_sum;
    }
}

}  // namespace moe
}  // namespace omni
