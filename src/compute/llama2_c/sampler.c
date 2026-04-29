#include <stdlib.h>
#include <math.h>

// OMNI llama2.c: Token Sampler
// Implements Temperature scaling and Top-p (Nucleus) sampling for LLM token selection.
// Source: karpathy/llama2.c

typedef struct {
    float prob;
    int index;
} ProbIndex;

// Helper for qsort
int compare_probindex(const void* a, const void* b) {
    float pa = ((ProbIndex*)a)->prob;
    float pb = ((ProbIndex*)b)->prob;
    if (pa > pb) return -1;
    if (pa < pb) return 1;
    return 0;
}

// Sample a token from a probability distribution
int sample_topp(float* probabilities, int vocab_size, float temperature, float topp) {
    // 1. Apply temperature
    if (temperature == 0.0f) {
        // Greedy argmax
        int best_idx = 0;
        float best_prob = probabilities[0];
        for (int i = 1; i < vocab_size; i++) {
            if (probabilities[i] > best_prob) {
                best_prob = probabilities[i];
                best_idx = i;
            }
        }
        return best_idx;
    }

    if (temperature != 1.0f) {
        float sum = 0.0f;
        for (int i = 0; i < vocab_size; i++) {
            probabilities[i] = powf(probabilities[i], 1.0f / temperature);
            sum += probabilities[i];
        }
        for (int i = 0; i < vocab_size; i++) {
            probabilities[i] /= sum; // Re-normalize
        }
    }

    // 2. Top-p (Nucleus) sampling
    if (topp <= 0.0f || topp >= 1.0f) {
        topp = 1.0f; // No filtering
    }

    ProbIndex* sorted_probs = (ProbIndex*)malloc(vocab_size * sizeof(ProbIndex));
    for (int i = 0; i < vocab_size; i++) {
        sorted_probs[i].prob = probabilities[i];
        sorted_probs[i].index = i;
    }

    qsort(sorted_probs, vocab_size, sizeof(ProbIndex), compare_probindex);

    float cumulative_prob = 0.0f;
    int cutoff_index = 0;
    for (int i = 0; i < vocab_size; i++) {
        cumulative_prob += sorted_probs[i].prob;
        if (cumulative_prob >= topp) {
            cutoff_index = i;
            break;
        }
    }

    // Renormalize the truncated distribution
    float new_sum = 0.0f;
    for (int i = 0; i <= cutoff_index; i++) {
        new_sum += sorted_probs[i].prob;
    }

    // Sample from the truncated distribution
    float r = ((float)rand() / (float)RAND_MAX) * new_sum;
    float current_sum = 0.0f;
    int selected_token = sorted_probs[cutoff_index].index; // Fallback

    for (int i = 0; i <= cutoff_index; i++) {
        current_sum += sorted_probs[i].prob;
        if (r <= current_sum) {
            selected_token = sorted_probs[i].index;
            break;
        }
    }

    free(sorted_probs);
    return selected_token;
}
