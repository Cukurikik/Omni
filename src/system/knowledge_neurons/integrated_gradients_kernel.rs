/// @omni-layer System | @omni-source EleutherAI/knowledge-neurons | @omni-lang Rust
/// @omni-description Integrated gradients kernel: lock-free attribution
/// computation for knowledge neuron localization in transformer FFN layers.
use std::sync::atomic::{AtomicUsize, Ordering};

#[derive(Debug)]
pub enum IGError { InvalidLayer(usize), EmptyActivations }
pub type OmniResult<T> = Result<T, IGError>;

pub struct NeuronAttribution {
    pub layer: usize,
    pub neuron: usize,
    pub attribution: f64,
}

pub struct IntegratedGradientsKernel {
    n_layers: usize,
    d_ffn: usize,
    n_steps: usize,
    computed: AtomicUsize,
}

impl IntegratedGradientsKernel {
    pub fn new(n_layers: usize, d_ffn: usize, n_steps: usize) -> Self {
        Self { n_layers, d_ffn, n_steps, computed: AtomicUsize::new(0) }
    }

    fn relu(x: f64) -> f64 { if x > 0.0 { x } else { 0.0 } }

    pub fn compute_attribution(&self, layer: usize, neuron: usize, baseline: f64, target: f64, weight: f64) -> OmniResult<f64> {
        if layer >= self.n_layers { return Err(IGError::InvalidLayer(layer)); }
        let mut total_grad = 0.0;
        for step in 0..self.n_steps {
            let alpha = step as f64 / (self.n_steps - 1).max(1) as f64;
            let interpolated = baseline + alpha * (target - baseline);
            let act = Self::relu(interpolated * weight);
            let act_delta = Self::relu((interpolated + 1e-4) * weight);
            let grad = (act_delta - act) / 1e-4;
            total_grad += grad;
        }
        let ig = (target - baseline) * total_grad / self.n_steps as f64;
        self.computed.fetch_add(1, Ordering::Relaxed);
        Ok(ig)
    }

    pub fn scan_layer(&self, layer: usize, baseline: f64, target: f64, weights: &[f64]) -> OmniResult<Vec<NeuronAttribution>> {
        if layer >= self.n_layers { return Err(IGError::InvalidLayer(layer)); }
        let mut attrs = Vec::with_capacity(weights.len());
        for (neuron, &w) in weights.iter().enumerate() {
            let ig = self.compute_attribution(layer, neuron, baseline, target, w)?;
            if ig.abs() > 1e-6 {
                attrs.push(NeuronAttribution { layer, neuron, attribution: ig.abs() });
            }
        }
        attrs.sort_by(|a, b| b.attribution.partial_cmp(&a.attribution).unwrap());
        Ok(attrs)
    }

    pub fn total_computed(&self) -> usize { self.computed.load(Ordering::Relaxed) }
}
