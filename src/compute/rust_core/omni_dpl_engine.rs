// BATCH 36: DPL Engine
// OMNI FRAMEWORK COMPLIANT - ZERO MOCK - MONADIC ERROR HANDLING
// COMPUTE LAYER - RUST

#[derive(Debug)]
pub enum DplError {
    InvalidPolicyGradient,
}

pub struct OmniDplEngine {
    learning_rate: f32,
}

impl OmniDplEngine {
    pub fn new(lr: f32) -> Result<Self, DplError> {
        if lr <= 0.0 || lr >= 1.0 { return Err(DplError::InvalidPolicyGradient); }
        Ok(Self { learning_rate: lr })
    }

    pub fn apply_policy_update(&self, reward_signal: f32, base_weight: f32) -> Result<f32, DplError> {
        if reward_signal.is_nan() || base_weight.is_nan() {
            return Err(DplError::InvalidPolicyGradient);
        }

        // Direct Policy Learning update step
        let delta = reward_signal * self.learning_rate;
        let updated = base_weight + delta;

        if updated.is_infinite() || updated.is_nan() {
            return Err(DplError::InvalidPolicyGradient);
        }

        Ok(updated)
    }
}
