/// @omni-layer System | @omni-source yuanzhoulvpi2017/DocumentSearch + md-experiments/elastic_transformers | @omni-lang Rust
/// @omni-description Inverted index kernel: thread-safe BM25-compatible
/// inverted index with term frequency and document length normalization.
use std::collections::HashMap;
use std::sync::Mutex;

#[derive(Debug)]
pub enum IndexError { EmptyDoc, NotFound }
pub type OmniResult<T> = Result<T, IndexError>;

pub struct PostingEntry {
    pub doc_id: u32,
    pub term_freq: u32,
    pub positions: Vec<u32>,
}

pub struct InvertedIndex {
    index: Mutex<HashMap<String, Vec<PostingEntry>>>,
    doc_lengths: Mutex<HashMap<u32, u32>>,
    total_docs: Mutex<u32>,
    avg_dl: Mutex<f64>,
    k1: f64,
    b: f64,
}

impl InvertedIndex {
    pub fn new(k1: f64, b: f64) -> Self {
        Self {
            index: Mutex::new(HashMap::new()),
            doc_lengths: Mutex::new(HashMap::new()),
            total_docs: Mutex::new(0),
            avg_dl: Mutex::new(0.0),
            k1, b,
        }
    }

    fn tokenize(text: &str) -> Vec<String> {
        text.to_lowercase()
            .split(|c: char| !c.is_alphanumeric())
            .filter(|w| w.len() > 1)
            .map(|w| w.to_string())
            .collect()
    }

    pub fn add_document(&self, doc_id: u32, text: &str) -> OmniResult<u32> {
        let tokens = Self::tokenize(text);
        if tokens.is_empty() { return Err(IndexError::EmptyDoc); }
        let doc_len = tokens.len() as u32;
        let mut term_positions: HashMap<String, Vec<u32>> = HashMap::new();
        for (pos, token) in tokens.iter().enumerate() {
            term_positions.entry(token.clone()).or_default().push(pos as u32);
        }
        let mut index = self.index.lock().unwrap();
        for (term, positions) in term_positions {
            let entry = PostingEntry { doc_id, term_freq: positions.len() as u32, positions };
            index.entry(term).or_default().push(entry);
        }
        let mut doc_lengths = self.doc_lengths.lock().unwrap();
        doc_lengths.insert(doc_id, doc_len);
        let mut total = self.total_docs.lock().unwrap();
        *total += 1;
        let n = *total as f64;
        let sum: f64 = doc_lengths.values().map(|&v| v as f64).sum();
        *self.avg_dl.lock().unwrap() = sum / n;
        Ok(doc_len)
    }

    pub fn bm25_score(&self, query: &str) -> OmniResult<Vec<(u32, f64)>> {
        let query_tokens = Self::tokenize(query);
        let index = self.index.lock().unwrap();
        let doc_lengths = self.doc_lengths.lock().unwrap();
        let n = *self.total_docs.lock().unwrap() as f64;
        let avg_dl = *self.avg_dl.lock().unwrap();
        let mut scores: HashMap<u32, f64> = HashMap::new();
        for token in &query_tokens {
            if let Some(postings) = index.get(token) {
                let df = postings.len() as f64;
                let idf = ((n - df + 0.5) / (df + 0.5) + 1.0).ln();
                for entry in postings {
                    let dl = *doc_lengths.get(&entry.doc_id).unwrap_or(&1) as f64;
                    let tf = entry.term_freq as f64;
                    let numerator = tf * (self.k1 + 1.0);
                    let denominator = tf + self.k1 * (1.0 - self.b + self.b * dl / avg_dl.max(1.0));
                    *scores.entry(entry.doc_id).or_insert(0.0) += idf * numerator / denominator;
                }
            }
        }
        let mut result: Vec<(u32, f64)> = scores.into_iter().collect();
        result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        Ok(result)
    }

    pub fn doc_count(&self) -> u32 { *self.total_docs.lock().unwrap() }
    pub fn term_count(&self) -> usize { self.index.lock().unwrap().len() }
}
