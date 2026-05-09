// OMNI Framework - Smashed Dataset Transformer in Rust
// Zero-mock implementation for high-speed dataset tokenization and batching.

use std::collections::HashMap;
use std::sync::Arc;

pub struct OmniSmashedConfig {
    pub max_seq_len: usize,
    pub batch_size: usize,
    pub padding_token: u32,
}

pub struct DatasetRecord {
    pub text: String,
    pub label: i32,
}

pub struct TokenizedBatch {
    pub input_ids: Vec<Vec<u32>>,
    pub attention_masks: Vec<Vec<u8>>,
    pub labels: Vec<i32>,
}

pub struct OmniSmashedPipeline {
    config: OmniSmashedConfig,
    vocab: Arc<HashMap<String, u32>>,
}

impl OmniSmashedPipeline {
    pub fn new(config: OmniSmashedConfig, vocab: HashMap<String, u32>) -> Self {
        Self {
            config,
            vocab: Arc::new(vocab),
        }
    }

    fn tokenize(&self, text: &str) -> Vec<u32> {
        let mut tokens = Vec::new();
        for word in text.split_whitespace() {
            let token_id = self.vocab.get(word).copied().unwrap_or(0); // 0 = UNK
            tokens.push(token_id);
            if tokens.len() >= self.config.max_seq_len {
                break;
            }
        }
        
        // Pad sequence
        while tokens.len() < self.config.max_seq_len {
            tokens.push(self.config.padding_token);
        }
        tokens
    }

    pub fn process_batch(&self, records: &[DatasetRecord]) -> TokenizedBatch {
        let mut input_ids = Vec::with_capacity(records.len());
        let mut attention_masks = Vec::with_capacity(records.len());
        let mut labels = Vec::with_capacity(records.len());

        for record in records {
            let tokens = self.tokenize(&record.text);
            let mask: Vec<u8> = tokens.iter()
                .map(|&t| if t == self.config.padding_token { 0 } else { 1 })
                .collect();

            input_ids.push(tokens);
            attention_masks.push(mask);
            labels.push(record.label);
        }

        TokenizedBatch {
            input_ids,
            attention_masks,
            labels,
        }
    }
}
