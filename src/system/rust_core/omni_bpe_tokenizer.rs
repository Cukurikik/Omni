// OMNI System — Rust BPE Tokenizer
// High-performance byte-pair encoding tokenizer for inference.

use std::collections::HashMap;

pub struct BPETokenizer {
    vocab: HashMap<String, u32>,
    merges: Vec<(String, String)>,
    id_to_token: HashMap<u32, String>,
    special_tokens: HashMap<String, u32>,
    vocab_size: usize,
}

impl BPETokenizer {
    pub fn new() -> Self {
        let mut tokenizer = Self {
            vocab: HashMap::new(),
            merges: Vec::new(),
            id_to_token: HashMap::new(),
            special_tokens: HashMap::new(),
            vocab_size: 0,
        };
        // Initialize base vocabulary (byte-level)
        for byte in 0u8..=255 {
            let token = format!("{}", byte as char);
            let id = byte as u32;
            tokenizer.vocab.insert(token.clone(), id);
            tokenizer.id_to_token.insert(id, token);
        }
        tokenizer.vocab_size = 256;
        // Add special tokens
        for (token, id) in [("<|pad|>", 0u32), ("<|bos|>", 1), ("<|eos|>", 2), ("<|unk|>", 3)] {
            tokenizer.special_tokens.insert(token.to_string(), id);
        }
        tokenizer
    }

    pub fn add_merge(&mut self, a: &str, b: &str) {
        let merged = format!("{}{}", a, b);
        if !self.vocab.contains_key(&merged) {
            let id = self.vocab_size as u32;
            self.vocab.insert(merged.clone(), id);
            self.id_to_token.insert(id, merged);
            self.vocab_size += 1;
        }
        self.merges.push((a.to_string(), b.to_string()));
    }

    pub fn encode(&self, text: &str) -> Vec<u32> {
        let mut tokens: Vec<String> = text.chars().map(|c| c.to_string()).collect();

        // Apply merges greedily
        for (a, b) in &self.merges {
            let mut i = 0;
            while i + 1 < tokens.len() {
                if tokens[i] == *a && tokens[i + 1] == *b {
                    tokens[i] = format!("{}{}", a, b);
                    tokens.remove(i + 1);
                } else {
                    i += 1;
                }
            }
        }

        tokens.iter()
            .map(|t| *self.vocab.get(t).unwrap_or(&3)) // 3 = <|unk|>
            .collect()
    }

    pub fn decode(&self, ids: &[u32]) -> String {
        ids.iter()
            .filter_map(|id| self.id_to_token.get(id))
            .cloned()
            .collect()
    }

    pub fn encode_batch(&self, texts: &[&str]) -> Vec<Vec<u32>> {
        texts.iter().map(|t| self.encode(t)).collect()
    }

    pub fn vocab_size(&self) -> usize { self.vocab_size }

    pub fn token_to_id(&self, token: &str) -> Option<u32> {
        self.vocab.get(token).copied()
            .or_else(|| self.special_tokens.get(token).copied())
    }

    pub fn id_to_token(&self, id: u32) -> Option<&str> {
        self.id_to_token.get(&id).map(|s| s.as_str())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_encoding() {
        let tokenizer = BPETokenizer::new();
        let ids = tokenizer.encode("hello");
        assert_eq!(ids.len(), 5);
    }

    #[test]
    fn test_roundtrip() {
        let tokenizer = BPETokenizer::new();
        let text = "abc";
        let ids = tokenizer.encode(text);
        let decoded = tokenizer.decode(&ids);
        assert_eq!(text, decoded);
    }

    #[test]
    fn test_merge() {
        let mut tokenizer = BPETokenizer::new();
        tokenizer.add_merge("h", "e");
        let ids = tokenizer.encode("hello");
        assert!(ids.len() < 5); // "he" merged
    }
}
