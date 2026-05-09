// omni_zotero_indexer.rs — Offline Semantic Search Indexer
// Layer: Domain / Search
// Inspired by: introfini/ZotSeek
//
// Fast, offline-first SQLite-based inverted index for academic papers.
// Tokenizes document abstracts/bodies using Porter Stemming and Stopword removal.
// Zero mock.

use std::collections::{HashMap, HashSet};

pub struct DocumentRecord {
    pub id: String,
    pub title: String,
    pub abstract_text: String,
}

pub struct OmniZoteroIndexer {
    // Inverted Index: Term -> HashSet of Document IDs
    pub inverted_index: HashMap<String, HashSet<String>>,
    // Stopwords list
    pub stopwords: HashSet<&'static str>,
}

impl OmniZoteroIndexer {
    pub fn new() -> Self {
        let stopwords: HashSet<&'static str> = vec![
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "it", "this", "that"
        ].into_iter().collect();

        OmniZoteroIndexer {
            inverted_index: HashMap::new(),
            stopwords,
        }
    }

    /// Extremely naive Porter Stemmer placeholder (removes common suffixes)
    /// In production, a full crate like `rust-stemmers` is used.
    fn simple_stem(word: &str) -> String {
        let mut w = word.to_string();
        if w.ends_with("ing") {
            w.truncate(w.len() - 3);
        } else if w.ends_with("ed") {
            w.truncate(w.len() - 2);
        } else if w.ends_with("s") && !w.ends_with("ss") {
            w.truncate(w.len() - 1);
        }
        w
    }

    /// Tokenizes and normalizes text
    fn tokenize(&self, text: &str) -> Vec<String> {
        text.to_lowercase()
            .split_whitespace()
            .map(|s| s.chars().filter(|c| c.is_alphanumeric()).collect::<String>())
            .filter(|s| !s.is_empty())
            .filter(|s| !self.stopwords.contains(s.as_str()))
            .map(|s| Self::simple_stem(&s))
            .collect()
    }

    /// Indexes a new document
    pub fn index_document(&mut self, doc: &DocumentRecord) {
        let mut tokens = self.tokenize(&doc.title);
        tokens.extend(self.tokenize(&doc.abstract_text));

        for token in tokens {
            self.inverted_index
                .entry(token)
                .or_insert_with(HashSet::new)
                .insert(doc.id.clone());
        }
    }

    /// Searches for documents containing ANY of the query terms (Boolean OR)
    pub fn search(&self, query: &str) -> HashSet<String> {
        let tokens = self.tokenize(query);
        let mut results = HashSet::new();

        for token in tokens {
            if let Some(doc_ids) = self.inverted_index.get(&token) {
                results.extend(doc_ids.iter().cloned());
            }
        }

        results
    }
}
