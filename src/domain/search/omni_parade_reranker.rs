// omni_parade_reranker.rs — Passage Representation Aggregation (PARADE)
// Layer: Domain / Search
// Inspired by: canjiali/PARADE
//
// Implements document re-ranking by aggregating passage-level representations
// outputted by a cross-encoder (like BERT). Zero mock.

use std::cmp::Ordering;

#[derive(Debug, Clone)]
pub struct Passage {
    pub id: String,
    pub score: f64,
    pub representation: Vec<f64>, // [CLS] embedding from Cross-Encoder
}

#[derive(Debug, Clone)]
pub struct Document {
    pub id: String,
    pub passages: Vec<Passage>,
    pub final_score: f64,
}

pub struct OmniParadeReranker {
    pub max_passages_per_doc: usize,
    pub strategy: AggregationStrategy,
}

#[derive(Debug, PartialEq)]
pub enum AggregationStrategy {
    MaxP,        // PARADE-Max: Take the maximum passage score
    AvgP,        // PARADE-Avg: Take the average of passage scores
    Attention,   // PARADE-Attn: Aggregate using a simulated attention layer (simplified here via dot product to a query vector)
}

impl OmniParadeReranker {
    pub fn new(max_passages_per_doc: usize, strategy: AggregationStrategy) -> Self {
        OmniParadeReranker {
            max_passages_per_doc,
            strategy,
        }
    }

    /// Reranks a list of documents based on their passage representations.
    pub fn rerank(&self, mut documents: Vec<Document>, query_embedding: Option<&[f64]>) -> Vec<Document> {
        for doc in &mut documents {
            // Sort passages by base score descending, keep top K
            doc.passages.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap_or(Ordering::Equal));
            
            let passages_to_use = if doc.passages.len() > self.max_passages_per_doc {
                &doc.passages[0..self.max_passages_per_doc]
            } else {
                &doc.passages[..]
            };

            if passages_to_use.is_empty() {
                doc.final_score = f64::NEG_INFINITY;
                continue;
            }

            // Apply PARADE aggregation strategy
            doc.final_score = match self.strategy {
                AggregationStrategy::MaxP => {
                    passages_to_use[0].score // Since they are sorted, [0] is max
                }
                AggregationStrategy::AvgP => {
                    let sum: f64 = passages_to_use.iter().map(|p| p.score).sum();
                    sum / (passages_to_use.len() as f64)
                }
                AggregationStrategy::Attention => {
                    if let Some(query_emb) = query_embedding {
                        let mut weighted_sum = 0.0;
                        let mut total_weight = 0.0;

                        for p in passages_to_use {
                            // Compute attention weight (dot product of passage representation and query embedding)
                            let weight: f64 = p.representation.iter().zip(query_emb.iter())
                                .map(|(a, b)| a * b)
                                .sum();
                            
                            // Exponential for softmax simulation
                            let exp_weight = weight.exp();
                            weighted_sum += p.score * exp_weight;
                            total_weight += exp_weight;
                        }
                        
                        if total_weight > 0.0 {
                            weighted_sum / total_weight
                        } else {
                            0.0
                        }
                    } else {
                        // Fallback to MaxP if no query embedding is provided
                        passages_to_use[0].score
                    }
                }
            };
        }

        // Final sort of documents based on the aggregated score
        documents.sort_by(|a, b| b.final_score.partial_cmp(&a.final_score).unwrap_or(Ordering::Equal));
        documents
    }
}
