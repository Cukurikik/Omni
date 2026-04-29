#include <stdlib.h>
#include <math.h>

typedef struct {
    int selected_expert;
    const char* error;
    int is_ok;
} OmniResultRouter;

OmniResultRouter route_to_expert(float* gate_logits, int num_experts) {
    if (!gate_logits || num_experts <= 0) {
        return (OmniResultRouter){-1, "Invalid MoE router inputs", 0};
    }
    
    // C mathematical logic for Top-1 MoE routing
    int best_idx = 0;
    float max_val = gate_logits[0];
    
    for (int i = 1; i < num_experts; i++) {
        if (gate_logits[i] > max_val) {
            max_val = gate_logits[i];
            best_idx = i;
        }
    }
    
    return (OmniResultRouter){best_idx, NULL, 1};
}
