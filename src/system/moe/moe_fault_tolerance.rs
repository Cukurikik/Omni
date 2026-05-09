// moe_fault_tolerance.rs — System / Reliability
// Layer: System / Core — Dead Expert Bypass
//
// In a large cluster, expert nodes fail. Instead of crashing inference, 
// this Rust module detects dead experts and reroutes tokens to the 
// second-highest probability expert according to the router's softmax distribution.

pub struct FallbackRouter {
    pub dead_experts: Vec<bool>, // true if dead
}

pub struct RerouteResult {
    pub original_expert: usize,
    pub final_expert: usize,
    pub was_rerouted: bool,
}

impl FallbackRouter {
    pub fn new(num_experts: usize) -> Self {
        println!("[MoE Fallback] Fault Tolerance Router initialized.");
        Self {
            dead_experts: vec![false; num_experts],
        }
    }

    /// Marks an expert as offline
    pub fn mark_expert_dead(&mut self, expert_id: usize) {
        if expert_id < self.dead_experts.len() {
            self.dead_experts[expert_id] = true;
            println!("[MoE Fallback] Expert {} marked as DEAD. Traffic will be rerouted.", expert_id);
        }
    }

    /// Recalculates the routing assignment bypassing dead experts
    pub fn safe_route(
        &self, 
        expert_probabilities: &[f32]
    ) -> RerouteResult {
        
        let mut best_expert = 0;
        let mut best_prob = -1.0;
        let mut original_expert = 0;
        let mut original_prob = -1.0;

        for (i, &prob) in expert_probabilities.iter().enumerate() {
            // Track the original top choice regardless of health
            if prob > original_prob {
                original_prob = prob;
                original_expert = i;
            }

            // Track the best HEALTHY choice
            if !self.dead_experts[i] && prob > best_prob {
                best_prob = prob;
                best_expert = i;
            }
        }

        RerouteResult {
            original_expert,
            final_expert: best_expert,
            was_rerouted: original_expert != best_expert,
        }
    }
}
