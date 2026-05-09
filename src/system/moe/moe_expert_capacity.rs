// moe_expert_capacity.rs — System / Routing
// Layer: System / Core — Expert Capacity Enforcer
//
// MoE models drop tokens if an expert is assigned too many tokens
// (Capacity Factor = C). This Rust module strictly enforces token capacity limits
// during the scatter operation, returning dropped tokens to be handled via residual connections.

pub struct ExpertCapacityManager {
    num_experts: usize,
    capacity_factor: f64,
}

pub struct RoutingResult {
    pub accepted_tokens: Vec<usize>, // Token indices accepted
    pub dropped_tokens: Vec<usize>,  // Token indices dropped due to overflow
}

impl ExpertCapacityManager {
    pub fn new(num_experts: usize, capacity_factor: f64) -> Self {
        Self {
            num_experts,
            capacity_factor,
        }
    }

    /// Enforces the capacity limit on a batch of token routing assignments.
    /// Returns which tokens were accepted and which were dropped.
    pub fn enforce_capacity(
        &self, 
        tokens_per_batch: usize, 
        expert_assignments: &[usize]
    ) -> Vec<RoutingResult> {
        
        // Calculate max tokens allowed per expert
        // Capacity = (Tokens in batch / Num Experts) * Capacity Factor
        let max_capacity = ((tokens_per_batch as f64 / self.num_experts as f64) * self.capacity_factor).ceil() as usize;
        
        let mut results = Vec::with_capacity(self.num_experts);
        for _ in 0..self.num_experts {
            results.push(RoutingResult {
                accepted_tokens: Vec::new(),
                dropped_tokens: Vec::new(),
            });
        }

        // Keep track of current load per expert
        let mut current_loads = vec![0; self.num_experts];

        // Process assignments
        for (token_idx, &expert_id) in expert_assignments.iter().enumerate() {
            if expert_id >= self.num_experts {
                continue; // Safety check
            }

            if current_loads[expert_id] < max_capacity {
                // Accept
                results[expert_id].accepted_tokens.push(token_idx);
                current_loads[expert_id] += 1;
            } else {
                // Overflow -> Drop token
                results[expert_id].dropped_tokens.push(token_idx);
            }
        }

        results
    }
}
