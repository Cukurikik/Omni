// omni_document_parser.rs — Document Cleaner & Tokenizer
// Layer: Domain / Rust
//
// Implements an extremely fast text extraction and normalization pipeline
// for removing HTML tags and markdown artifacts before indexing. Zero mock.

use std::collections::HashSet;

pub struct OmniDocumentParser {
    stop_words: HashSet<String>,
}

impl OmniDocumentParser {
    pub fn new(custom_stop_words: Option<Vec<String>>) -> Self {
        let mut stop_words = HashSet::new();
        let default_stop_words = vec![
            "the", "and", "a", "an", "in", "is", "it", "to", "of", "for", "on", "with"
        ];
        
        for w in default_stop_words {
            stop_words.insert(w.to_string());
        }

        if let Some(custom) = custom_stop_words {
            for w in custom {
                stop_words.insert(w.to_lowercase());
            }
        }

        OmniDocumentParser { stop_words }
    }

    /// Strips HTML tags using a fast iterative state machine.
    pub fn strip_html(input: &str) -> String {
        let mut result = String::with_capacity(input.len());
        let mut in_tag = false;

        for c in input.chars() {
            match c {
                '<' => in_tag = true,
                '>' => in_tag = false,
                _ => {
                    if !in_tag {
                        result.push(c);
                    }
                }
            }
        }
        result
    }

    /// Cleans special markdown characters.
    pub fn strip_markdown(input: &str) -> String {
        let mut result = String::with_capacity(input.len());
        for c in input.chars() {
            if c != '*' && c != '#' && c != '`' && c != '_' {
                result.push(c);
            }
        }
        result
    }

    /// Normalizes, strips markup, tokenizes, and removes stop words.
    pub fn parse_and_tokenize(&self, document: &str) -> Vec<String> {
        let no_html = Self::strip_html(document);
        let no_md = Self::strip_markdown(&no_html);
        
        // Lowercase and split on non-alphanumeric boundaries
        let mut tokens = Vec::new();
        let mut current_token = String::new();

        for c in no_md.chars() {
            if c.is_alphanumeric() {
                current_token.push(c.to_ascii_lowercase());
            } else if !current_token.is_empty() {
                if !self.stop_words.contains(&current_token) {
                    tokens.push(current_token.clone());
                }
                current_token.clear();
            }
        }

        if !current_token.is_empty() && !self.stop_words.contains(&current_token) {
            tokens.push(current_token);
        }

        tokens
    }
}
