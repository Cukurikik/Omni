// moe_deterministic_replay.rs — Deterministic Replay for MoE Debugging
// Layer: System / Debug — MoE Reproducibility
//
// Records and replays MoE routing decisions for deterministic
// debugging. Captures router inputs/outputs, expert selections,
// and random state to enable exact reproduction of any inference.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone)]
pub struct RoutingDecision {
    pub token_id: u32,
    pub expert_ids: Vec<u16>,
    pub weights: Vec<f32>,
    pub logits: Vec<f32>,
    pub rng_seed: u64,
}

#[derive(Debug, Clone)]
pub struct InferenceFrame {
    pub frame_id: u64,
    pub timestamp_us: u64,
    pub batch_size: u32,
    pub seq_len: u32,
    pub routing_decisions: Vec<RoutingDecision>,
    pub metadata: HashMap<String, String>,
}

impl InferenceFrame {
    pub fn new(frame_id: u64, batch_size: u32, seq_len: u32) -> Self {
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_micros() as u64;

        Self {
            frame_id,
            timestamp_us: ts,
            batch_size,
            seq_len,
            routing_decisions: Vec::new(),
            metadata: HashMap::new(),
        }
    }

    pub fn add_decision(&mut self, decision: RoutingDecision) {
        self.routing_decisions.push(decision);
    }

    pub fn set_metadata(&mut self, key: &str, value: &str) {
        self.metadata.insert(key.to_string(), value.to_string());
    }

    pub fn num_decisions(&self) -> usize {
        self.routing_decisions.len()
    }

    /// Get expert usage distribution for this frame.
    pub fn expert_distribution(&self, num_experts: u16) -> Vec<f64> {
        let mut counts = vec![0u64; num_experts as usize];
        for dec in &self.routing_decisions {
            for &eid in &dec.expert_ids {
                if (eid as usize) < counts.len() {
                    counts[eid as usize] += 1;
                }
            }
        }
        let total = counts.iter().sum::<u64>() as f64;
        if total == 0.0 {
            return vec![0.0; num_experts as usize];
        }
        counts.iter().map(|&c| c as f64 / total).collect()
    }
}

/// Replay buffer that records and replays inference frames.
pub struct ReplayBuffer {
    frames: Mutex<Vec<InferenceFrame>>,
    max_frames: usize,
    next_frame_id: Mutex<u64>,
    is_recording: Mutex<bool>,
}

impl ReplayBuffer {
    pub fn new(max_frames: usize) -> Self {
        Self {
            frames: Mutex::new(Vec::with_capacity(max_frames)),
            max_frames,
            next_frame_id: Mutex::new(0),
            is_recording: Mutex::new(false),
        }
    }

    /// Start recording inference frames.
    pub fn start_recording(&self) {
        *self.is_recording.lock().unwrap() = true;
    }

    /// Stop recording.
    pub fn stop_recording(&self) {
        *self.is_recording.lock().unwrap() = false;
    }

    /// Check if currently recording.
    pub fn is_recording(&self) -> bool {
        *self.is_recording.lock().unwrap()
    }

    /// Record a new inference frame.
    pub fn record_frame(&self, frame: InferenceFrame) -> u64 {
        if !self.is_recording() {
            return frame.frame_id;
        }

        let mut frames = self.frames.lock().unwrap();
        if frames.len() >= self.max_frames {
            frames.remove(0);
        }
        let id = frame.frame_id;
        frames.push(frame);
        id
    }

    /// Create a new frame with auto-incrementing ID.
    pub fn new_frame(&self, batch_size: u32, seq_len: u32) -> InferenceFrame {
        let mut next = self.next_frame_id.lock().unwrap();
        let id = *next;
        *next += 1;
        InferenceFrame::new(id, batch_size, seq_len)
    }

    /// Retrieve a frame by ID for replay.
    pub fn get_frame(&self, frame_id: u64) -> Option<InferenceFrame> {
        let frames = self.frames.lock().unwrap();
        frames.iter().find(|f| f.frame_id == frame_id).cloned()
    }

    /// Get the last N frames.
    pub fn last_n_frames(&self, n: usize) -> Vec<InferenceFrame> {
        let frames = self.frames.lock().unwrap();
        let start = if frames.len() > n { frames.len() - n } else { 0 };
        frames[start..].to_vec()
    }

    /// Find frames where a specific expert was activated.
    pub fn frames_with_expert(&self, expert_id: u16) -> Vec<u64> {
        let frames = self.frames.lock().unwrap();
        frames.iter()
            .filter(|f| f.routing_decisions.iter()
                .any(|d| d.expert_ids.contains(&expert_id)))
            .map(|f| f.frame_id)
            .collect()
    }

    /// Get total number of recorded frames.
    pub fn num_frames(&self) -> usize {
        self.frames.lock().unwrap().len()
    }

    /// Clear all recorded frames.
    pub fn clear(&self) {
        self.frames.lock().unwrap().clear();
    }

    /// Export all frames as a serializable report.
    pub fn export_report(&self) -> String {
        let frames = self.frames.lock().unwrap();
        let mut report = format!("Replay Buffer Report: {} frames\n", frames.len());

        for frame in frames.iter() {
            report.push_str(&format!(
                "  Frame {} | ts={} | batch={} | seq={} | decisions={}\n",
                frame.frame_id, frame.timestamp_us,
                frame.batch_size, frame.seq_len,
                frame.routing_decisions.len()));
        }
        report
    }
}

/// Comparator for verifying deterministic replay.
pub struct ReplayVerifier;

impl ReplayVerifier {
    /// Verify that two frames have identical routing decisions.
    pub fn verify(original: &InferenceFrame, replay: &InferenceFrame) -> ReplayVerification {
        let mut mismatches = Vec::new();

        if original.routing_decisions.len() != replay.routing_decisions.len() {
            return ReplayVerification {
                passed: false,
                mismatches: vec![format!(
                    "Decision count mismatch: {} vs {}",
                    original.routing_decisions.len(),
                    replay.routing_decisions.len())],
                total_decisions: original.routing_decisions.len(),
            };
        }

        for (i, (orig, rep)) in original.routing_decisions.iter()
            .zip(replay.routing_decisions.iter()).enumerate()
        {
            if orig.expert_ids != rep.expert_ids {
                mismatches.push(format!(
                    "Decision {}: expert_ids differ {:?} vs {:?}",
                    i, orig.expert_ids, rep.expert_ids));
            }
            // Check weights with tolerance
            for (j, (ow, rw)) in orig.weights.iter()
                .zip(rep.weights.iter()).enumerate()
            {
                if (ow - rw).abs() > 1e-5 {
                    mismatches.push(format!(
                        "Decision {} weight {}: {} vs {}",
                        i, j, ow, rw));
                }
            }
        }

        ReplayVerification {
            passed: mismatches.is_empty(),
            mismatches,
            total_decisions: original.routing_decisions.len(),
        }
    }
}

pub struct ReplayVerification {
    pub passed: bool,
    pub mismatches: Vec<String>,
    pub total_decisions: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_record_and_replay() {
        let buffer = ReplayBuffer::new(10);
        buffer.start_recording();

        let mut frame = buffer.new_frame(4, 128);
        frame.add_decision(RoutingDecision {
            token_id: 0,
            expert_ids: vec![2, 5],
            weights: vec![0.7, 0.3],
            logits: vec![0.1; 8],
            rng_seed: 42,
        });
        buffer.record_frame(frame);

        let retrieved = buffer.get_frame(0).unwrap();
        assert_eq!(retrieved.routing_decisions.len(), 1);
        assert_eq!(retrieved.routing_decisions[0].expert_ids, vec![2, 5]);
    }

    #[test]
    fn test_verify_determinism() {
        let mut frame1 = InferenceFrame::new(0, 1, 1);
        frame1.add_decision(RoutingDecision {
            token_id: 0, expert_ids: vec![1, 3],
            weights: vec![0.6, 0.4], logits: vec![], rng_seed: 0,
        });

        let frame2 = frame1.clone();
        let result = ReplayVerifier::verify(&frame1, &frame2);
        assert!(result.passed);
    }
}
