/// @omni-layer System | @omni-source hiyouga/Dual-Contrastive-Learning
/// @omni-description Contrastive loss kernel in Rust: vectorized cosine similarity
/// and NT-Xent loss computation for dual contrastive training.
/// @omni-lang Rust | @omni-batch 16 | @omni-semester 16

#[derive(Debug)]
pub enum CLError { EmptyBatch, DimensionMismatch }
pub type OmniResult<T> = Result<T, CLError>;

pub struct ContrastiveLossKernel { temperature: f64 }

impl ContrastiveLossKernel {
    pub fn new(temperature: f64) -> Self { Self { temperature } }

    pub fn cosine_similarity(a: &[f64], b: &[f64]) -> f64 {
        let d = a.len().min(b.len());
        let dot: f64 = (0..d).map(|i| a[i] * b[i]).sum();
        let na: f64 = a.iter().map(|x| x * x).sum::<f64>().sqrt();
        let nb: f64 = b.iter().map(|x| x * x).sum::<f64>().sqrt();
        dot / (na * nb + 1e-8)
    }

    pub fn nt_xent_loss(&self, embeddings: &[Vec<f64>], labels: &[usize]) -> OmniResult<f64> {
        if embeddings.is_empty() { return Err(CLError::EmptyBatch); }
        let n = embeddings.len();
        let mut total = 0.0f64;
        let mut count = 0usize;
        for i in 0..n {
            let positives: Vec<usize> = (0..n).filter(|&j| j != i && labels[j] == labels[i]).collect();
            if positives.is_empty() { continue; }
            for &p in &positives {
                let sim_pos = Self::cosine_similarity(&embeddings[i], &embeddings[p]) / self.temperature;
                let exp_sum: f64 = (0..n).filter(|&j| j != i)
                    .map(|j| (Self::cosine_similarity(&embeddings[i], &embeddings[j]) / self.temperature - sim_pos).exp())
                    .sum();
                total += (1.0 + exp_sum).ln();
                count += 1;
            }
        }
        Ok(if count > 0 { total / count as f64 } else { 0.0 })
    }

    pub fn similarity_matrix(embeddings: &[Vec<f64>]) -> OmniResult<Vec<Vec<f64>>> {
        if embeddings.is_empty() { return Err(CLError::EmptyBatch); }
        let n = embeddings.len();
        let mut matrix = vec![vec![0.0f64; n]; n];
        for i in 0..n { for j in 0..n { matrix[i][j] = Self::cosine_similarity(&embeddings[i], &embeddings[j]); } }
        Ok(matrix)
    }
}
