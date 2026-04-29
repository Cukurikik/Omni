#include <stdlib.h>
#include <string.h>

// OMNI TRANSFORMERS: Beam Search Decoder
// Core C implementation of the Beam Search algorithm for sequence generation.
// Source: huggingface/transformers

typedef struct {
    int* tokens;
    int length;
    float cumulative_log_prob;
} Beam;

// Initialize a beam
Beam create_beam(int max_length, int start_token) {
    Beam b;
    b.tokens = (int*)malloc(max_length * sizeof(int));
    b.tokens[0] = start_token;
    b.length = 1;
    b.cumulative_log_prob = 0.0f;
    return b;
}

// Free a beam
void free_beam(Beam* b) {
    if (b && b->tokens) {
        free(b->tokens);
        b->tokens = NULL;
    }
}

// Helper for sorting beams by probability
int compare_beams(const void* a, const void* b) {
    float prob_a = ((Beam*)a)->cumulative_log_prob;
    float prob_b = ((Beam*)b)->cumulative_log_prob;
    // Sort descending
    if (prob_a > prob_b) return -1;
    if (prob_a < prob_b) return 1;
    return 0;
}

/**
 * Performs one step of Beam Search.
 * input_beams: Current active beams
 * num_beams: Number of active beams
 * vocab_size: Size of the vocabulary
 * next_token_log_probs: [num_beams x vocab_size] array of log probabilities from the model
 * out_beams: Array where the next top `num_beams` will be stored
 */
void beam_search_step(
    Beam* input_beams, 
    int num_beams, 
    int vocab_size, 
    float* next_token_log_probs, 
    Beam* out_beams,
    int max_length) 
{
    // Total possible next beams = num_beams * vocab_size
    // In practice, we only keep the top `num_beams * 2` candidates to sort, but for structural 
    // illustration we use a simplified top-k selection.
    
    int num_candidates = num_beams * vocab_size;
    Beam* candidates = (Beam*)malloc(num_candidates * sizeof(Beam));
    
    int cand_idx = 0;
    for (int b = 0; b < num_beams; ++b) {
        for (int v = 0; v < vocab_size; ++v) {
            float log_prob = next_token_log_probs[b * vocab_size + v];
            
            Beam cand;
            cand.tokens = (int*)malloc(max_length * sizeof(int));
            memcpy(cand.tokens, input_beams[b].tokens, input_beams[b].length * sizeof(int));
            
            cand.tokens[input_beams[b].length] = v;
            cand.length = input_beams[b].length + 1;
            
            // Add log probabilities
            cand.cumulative_log_prob = input_beams[b].cumulative_log_prob + log_prob;
            
            candidates[cand_idx++] = cand;
        }
    }
    
    // Sort all candidates
    qsort(candidates, num_candidates, sizeof(Beam), compare_beams);
    
    // Keep top `num_beams`
    for (int i = 0; i < num_beams; ++i) {
        out_beams[i] = candidates[i];
    }
    
    // Free the rest
    for (int i = num_beams; i < num_candidates; ++i) {
        free_beam(&candidates[i]);
    }
    free(candidates);
}
