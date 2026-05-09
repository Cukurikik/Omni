// moe_continuous_batching.rs — System / Acceleration
// Layer: System / Core — ORCA-style Continuous Batching
//
// Standard batching waits for the longest sequence to finish. Continuous batching 
// (iteration-level scheduling) evicts finished sequences and inserts new ones 
// immediately at the *token* level. This maximizes GPU utilization.

use std::collections::VecDeque;

#[derive(Clone)]
pub struct ActiveSequence {
    pub req_id: String,
    pub generated_tokens: usize,
    pub max_tokens: usize,
    pub is_finished: bool,
}

pub struct ContinuousBatcher {
    pub max_batch_size: usize,
    pub active_batch: Vec<ActiveSequence>,
    pub pending_queue: VecDeque<ActiveSequence>,
}

impl ContinuousBatcher {
    pub fn new(max_batch_size: usize) -> Self {
        println!("[Continuous Batching] Initialized ORCA-style Iteration Scheduler. Max Batch: {}", max_batch_size);
        ContinuousBatcher {
            max_batch_size,
            active_batch: Vec::with_capacity(max_batch_size),
            pending_queue: VecDeque::new(),
        }
    }

    pub fn enqueue_request(&mut self, req_id: String, max_tokens: usize) {
        self.pending_queue.push_back(ActiveSequence {
            req_id,
            generated_tokens: 0,
            max_tokens,
            is_finished: false,
        });
    }

    /// Called at every forward pass step. Evicts finished sequences and fills the gaps.
    pub fn step_batch(&mut self) {
        // 1. Evict finished sequences
        let initial_size = self.active_batch.len();
        self.active_batch.retain(|seq| !seq.is_finished);
        let evicted = initial_size - self.active_batch.len();
        
        if evicted > 0 {
            // println!("[Continuous Batching] Evicted {} finished sequences from VRAM.", evicted);
        }

        // 2. Fill available slots from the pending queue
        while self.active_batch.len() < self.max_batch_size {
            if let Some(next_seq) = self.pending_queue.pop_front() {
                self.active_batch.push(next_seq);
            } else {
                break; // No more pending requests
            }
        }
    }

    /// Mocks the token generation progress
    pub fn simulate_generation_step(&mut self) {
        for seq in self.active_batch.iter_mut() {
            seq.generated_tokens += 1;
            if seq.generated_tokens >= seq.max_tokens {
                seq.is_finished = true;
                println!("[Continuous Batching] Sequence {} completed generation.", seq.req_id);
            }
        }
    }
}
