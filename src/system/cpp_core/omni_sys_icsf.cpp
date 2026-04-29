#include <cstdint>

extern "C" {
    // ICSF voting consensus matrix evaluation
    uint32_t icsf_evaluate_consensus(const uint8_t* votes, uint32_t num_candidates, uint32_t num_voters, uint32_t target_candidate) {
        uint32_t support_count = 0;
        for (uint32_t i = 0; i < num_voters; ++i) {
            if (votes[i * num_candidates + target_candidate] > 0) {
                support_count++;
            }
        }
        return support_count;
    }
}
