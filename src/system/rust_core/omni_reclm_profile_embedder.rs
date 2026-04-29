// Omni RecLM Profile Embedder (Rust)
// Ref: HKUDS/RecLM — ACL2025
pub struct ProfileEmbedding { pub user_emb: Vec<f64>, pub item_emb: Vec<f64> }
impl ProfileEmbedding {
    pub fn collaborative_score(&self, neighbor_embs: &[Vec<f64>], alpha: f64) -> f64 {
        let direct: f64 = self.user_emb.iter().zip(self.item_emb.iter()).map(|(a, b)| a * b).sum();
        if neighbor_embs.is_empty() { return direct; }
        let d = self.user_emb.len();
        let avg: Vec<f64> = (0..d).map(|i| neighbor_embs.iter().map(|n| n[i]).sum::<f64>() / neighbor_embs.len() as f64).collect();
        let neighbor_sim: f64 = self.user_emb.iter().zip(avg.iter()).map(|(a, b)| a * b).sum();
        direct + alpha * neighbor_sim
    }
}
