/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// SQL Injection Static Analyzer.
/// Fast, regex-free lexical scanner that intercepts common SQLi payloads 
/// before they hit the Domain/System ORM layers.

pub enum SqlAnalyzerResult {
    Safe,
    TautologyDetected,
    UnionInjectionDetected,
    CommentInjectionDetected,
}

pub struct SqlInjectionAnalyzer;

impl SqlInjectionAnalyzer {
    /// Scans a raw input string for malicious SQL sequences.
    pub fn scan_input(input: &str) -> SqlAnalyzerResult {
        let normalized = input.to_lowercase();
        
        // 1. Tautology Checks (e.g., '1'='1', or 1=1)
        if normalized.contains("1=1") || normalized.contains("1'='1") || normalized.contains("\"=\"") {
            return SqlAnalyzerResult::TautologyDetected;
        }

        // 2. UNION Based Injection
        // Scans for 'UNION SELECT' ensuring they are separate words
        if Self::contains_word_sequence(&normalized, "union", "select") {
             return SqlAnalyzerResult::UnionInjectionDetected;
        }

        // 3. Comment Injection
        // SQL comments '--' or '/*' used to truncate queries
        if normalized.contains("--") || normalized.contains("/*") {
            return SqlAnalyzerResult::CommentInjectionDetected;
        }

        SqlAnalyzerResult::Safe
    }

    /// Fast sequential word matching without allocating a split vector
    fn contains_word_sequence(input: &str, word1: &str, word2: &str) -> bool {
        if let Some(pos1) = input.find(word1) {
            let remainder = &input[pos1 + word1.len()..];
            if let Some(pos2) = remainder.find(word2) {
                // Ensure there is only whitespace between them
                let between = &remainder[..pos2];
                if between.trim().is_empty() {
                    return true;
                }
            }
        }
        false
    }
}
