// phase_router.rs — System / Reliability
// Layer: System / Core — Deterministic Phase Routing
//
// Inspired by phase_router_rs.
// A capacity-aware deterministic router for modern MoE systems.
// Instead of random assignment during contention, this router uses a
// deterministic phase-space calculation to drop or redirect tokens, 
// ensuring predictable latency profiles.

use std::collections::HashMap;

pub struct PhaseRouter {
    max_capacity_per_expert: usize,
    current_load: HashMap<usize, usize>,
}

pub struct RouteDecision {
    pub expert_id: usize,
    pub is_dropped: bool,
    pub latency_penalty_ms: u32,
}

impl PhaseRouter {
    pub fn new(max_capacity: usize) -> Self {
        println!("[PhaseRouter] Initialized with deterministic capacity of {} tokens/expert", max_capacity);
        PhaseRouter {
            max_capacity_per_expert: max_capacity,
            current_load: HashMap::new(),
        }
    }

    /// Routes a token based on its deterministic phase (hash) and current capacity
    pub fn route_token(&mut self, target_expert: usize, token_hash: u64) -> RouteDecision {
        let load = self.current_load.entry(target_expert).or_insert(0);
        
        if *load < self.max_capacity_per_expert {
            *load += 1;
            return RouteDecision {
                expert_id: target_expert,
                is_dropped: false,
                latency_penalty_ms: 0,
            };
        }

        // Capacity Exceeded: Deterministic Phase Backoff
        // If the token hash is even, we aggressively drop it.
        // If odd, we apply a strict latency penalty and force it through.
        if token_hash % 2 == 0 {
            RouteDecision {
                expert_id: target_expert,
                is_dropped: true,
                latency_penalty_ms: 0,
            }
        } else {
            *load += 1; // Force through with penalty
            RouteDecision {
                expert_id: target_expert,
                is_dropped: false,
                latency_penalty_ms: 50, // 50ms penalty for entering the overload phase
            }
        }
    }

    /// Resets the load counters at the end of a forward pass / batch
    pub fn reset_epoch(&mut self) {
        self.current_load.clear();
    }
}
