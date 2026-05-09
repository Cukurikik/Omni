/// @omni-layer System | @omni-source lucidrains/genie2-pytorch | @omni-lang Rust
/// @omni-description VQ-VAE codebook: lock-free vector quantization for video
/// frame tokenization with EMA codebook updates and commitment loss.
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(Debug)]
pub enum VQError { EmptyInput, CodebookExhausted }
pub type OmniResult<T> = Result<T, VQError>;

pub struct CodebookEntry {
    vector: Vec<f64>,
    usage_count: AtomicU64,
}

pub struct VQCodebook {
    entries: Vec<CodebookEntry>,
    dim: usize,
    ema_decay: f64,
}

impl VQCodebook {
    pub fn new(codebook_size: usize, dim: usize, ema_decay: f64) -> Self {
        let entries = (0..codebook_size).map(|i| {
            let vector = (0..dim).map(|j| ((i*dim+j) as f64 * 0.001).sin() * 0.1).collect();
            CodebookEntry { vector, usage_count: AtomicU64::new(0) }
        }).collect();
        Self { entries, dim, ema_decay }
    }

    pub fn quantize(&self, input: &[f64]) -> OmniResult<(usize, Vec<f64>, f64)> {
        if input.len() != self.dim { return Err(VQError::EmptyInput); }
        let mut best_idx = 0;
        let mut best_dist = f64::MAX;
        for (i, entry) in self.entries.iter().enumerate() {
            let dist: f64 = input.iter().zip(&entry.vector).map(|(a,b)| (a-b)*(a-b)).sum();
            if dist < best_dist { best_dist = dist; best_idx = i; }
        }
        self.entries[best_idx].usage_count.fetch_add(1, Ordering::Relaxed);
        let quantized = self.entries[best_idx].vector.clone();
        Ok((best_idx, quantized, best_dist))
    }

    pub fn commitment_loss(input: &[f64], quantized: &[f64]) -> f64 {
        input.iter().zip(quantized).map(|(a,b)| (a-b)*(a-b)).sum::<f64>() / input.len() as f64
    }

    pub fn batch_quantize(&self, batch: &[Vec<f64>]) -> OmniResult<Vec<usize>> {
        let mut indices = Vec::with_capacity(batch.len());
        for vec in batch {
            let (idx, _, _) = self.quantize(vec)?;
            indices.push(idx);
        }
        Ok(indices)
    }

    pub fn codebook_utilization(&self) -> f64 {
        let used = self.entries.iter().filter(|e| e.usage_count.load(Ordering::Relaxed) > 0).count();
        used as f64 / self.entries.len() as f64
    }
}
