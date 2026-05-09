/// OMNI AST Diff Analyzer
/// Fast syntactic diffing of code files before LLM review.

pub struct AstDiffAnalyzer {
    language: String,
}

impl AstDiffAnalyzer {
    pub fn new(language: &str) -> Self {
        Self {
            language: language.to_string(),
        }
    }

    pub fn compute_complexity_change(&self, old_code: &str, new_code: &str) -> Result<i32, &'static str> {
        // Zero-mock approximation of Cyclomatic Complexity change
        let old_cc = self.count_branches(old_code);
        let new_cc = self.count_branches(new_code);
        
        Ok((new_cc as i32) - (old_cc as i32))
    }

    fn count_branches(&self, code: &str) -> usize {
        let keywords = ["if ", "else", "for ", "while ", "match ", "switch"];
        let mut count = 0;
        
        for line in code.lines() {
            for kw in &keywords {
                if line.contains(kw) {
                    count += 1;
                }
            }
        }
        
        count
    }
}
