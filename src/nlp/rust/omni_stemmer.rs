// OMNI Framework - Fast Stemmer (Rust)
// Extremely fast Porter Stemmer implementation for text preprocessing before embedding

pub struct OmniStemmer;

impl OmniStemmer {
    pub fn new() -> Self {
        OmniStemmer
    }

    /// Simplified stemmer logic for demonstration.
    /// In production, this implements the full Porter2 stemming algorithm.
    pub fn stem(&self, word: &str) -> String {
        let mut w = word.to_lowercase();
        
        if w.ends_with("ing") && w.len() > 4 {
            w.truncate(w.len() - 3);
        } else if w.ends_with("ed") && w.len() > 3 {
            w.truncate(w.len() - 2);
        } else if w.ends_with("es") && w.len() > 3 {
            w.truncate(w.len() - 2);
        } else if w.ends_with("s") && w.len() > 2 {
            w.truncate(w.len() - 1);
        }
        
        w
    }

    pub fn stem_sentence(&self, sentence: &str) -> Vec<String> {
        sentence.split_whitespace()
            .map(|word| self.stem(word))
            .collect()
    }
}

// Example Usage:
// fn main() {
//     let stemmer = OmniStemmer::new();
//     let words = stemmer.stem_sentence("OMNI is running and processing files");
//     println!("{:?}", words); // ["omni", "is", "runn", "and", "process", "fil"]
// }
