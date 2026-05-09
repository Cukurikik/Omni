// omni_byte_pair_encoding.rs — High-Speed BPE Tokenizer
// Layer: Compute / Rust
//
// Implements a fast Byte-Pair Encoding (BPE) algorithm for tokenization.
// Zero-mock, capable of decoding and encoding using pre-computed merge rules.

use std::collections::{HashMap, HashSet};

pub struct OmniBPETokenizer {
    vocab: HashMap<String, u32>,
    bpe_merges: HashMap<(String, String), u32>,
    inverse_vocab: HashMap<u32, String>,
}

impl OmniBPETokenizer {
    pub fn new() -> Self {
        OmniBPETokenizer {
            vocab: HashMap::new(),
            bpe_merges: HashMap::new(),
            inverse_vocab: HashMap::new(),
        }
    }

    /// Loads pre-computed vocabulary and merge rules.
    pub fn load(&mut self, vocab: HashMap<String, u32>, merges: Vec<(String, String)>) {
        self.vocab = vocab.clone();
        for (id, token) in vocab {
            self.inverse_vocab.insert(id, token);
        }

        for (i, merge) in merges.into_iter().enumerate() {
            self.bpe_merges.insert(merge, i as u32);
        }
    }

    /// Helper to find adjacent pairs in a word.
    fn get_pairs(word: &[String]) -> HashSet<(String, String)> {
        let mut pairs = HashSet::new();
        if word.len() < 2 {
            return pairs;
        }
        for i in 0..word.len() - 1 {
            pairs.insert((word[i].clone(), word[i + 1].clone()));
        }
        pairs
    }

    /// Encodes a single word into subword tokens.
    pub fn encode_word(&self, word: &str) -> Vec<u32> {
        // Initial split into characters (often suffixed with </w> in real BPE, 
        // but kept simple here for structure representation)
        let mut chars: Vec<String> = word.chars().map(|c| c.to_string()).collect();
        
        if chars.is_empty() {
            return Vec::new();
        }

        loop {
            let pairs = Self::get_pairs(&chars);
            if pairs.is_empty() {
                break;
            }

            // Find the pair with the lowest merge rank
            let mut min_rank = u32::MAX;
            let mut best_pair = None;

            for pair in pairs {
                if let Some(&rank) = self.bpe_merges.get(&pair) {
                    if rank < min_rank {
                        min_rank = rank;
                        best_pair = Some(pair);
                    }
                }
            }

            if best_pair.is_none() {
                break; // No more eligible merges
            }

            let best = best_pair.unwrap();
            let mut new_chars = Vec::new();
            let mut i = 0;

            while i < chars.len() {
                if i < chars.len() - 1 && chars[i] == best.0 && chars[i + 1] == best.1 {
                    new_chars.push(format!("{}{}", best.0, best.1));
                    i += 2;
                } else {
                    new_chars.push(chars[i].clone());
                    i += 1;
                }
            }
            chars = new_chars;
        }

        chars.iter()
            .filter_map(|t| self.vocab.get(t).cloned())
            .collect()
    }

    /// Decodes a sequence of token IDs back into text.
    pub fn decode(&self, ids: &[u32]) -> String {
        let mut text = String::new();
        for id in ids {
            if let Some(token) = self.inverse_vocab.get(id) {
                text.push_str(token);
            }
        }
        // In practice, this would clean up </w> or   subword markers.
        text
    }
}
