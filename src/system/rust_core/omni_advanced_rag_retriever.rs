// Omni Advanced RAG Retriever (Rust)
// Ref: GURPREETKAURJETHRA/Advanced_RAG
pub fn reciprocal_rank_fusion(ranked_lists: &[Vec<String>], k: usize) -> Vec<(String, f64)> {
    let mut scores = std::collections::HashMap::new();
    for list in ranked_lists {
        for (rank, doc_id) in list.iter().enumerate() {
            let score = scores.entry(doc_id.clone()).or_insert(0.0f64);
            *score += 1.0 / (rank as f64 + k as f64);
        }
    }
    let mut result: Vec<_> = scores.into_iter().collect();
    result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
    result
}
