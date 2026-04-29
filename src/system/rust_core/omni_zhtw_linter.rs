// Omni ZHTW-MCP Linter (Rust)
// Ref: sysprog21/zhtw-mcp — MIT
pub struct LintIssue { pub pos: usize, pub found: String, pub suggestion: String }
pub fn lint_zhtw(text: &str) -> Vec<LintIssue> {
    let rules = [("的话","的話"),("并且","並且"),("学习","學習"),("软件","軟體"),("信息","資訊")];
    let mut issues = Vec::new();
    for (simplified, traditional) in &rules {
        let mut start = 0;
        while let Some(pos) = text[start..].find(simplified) {
            issues.push(LintIssue { pos: start + pos, found: simplified.to_string(), suggestion: traditional.to_string() });
            start += pos + simplified.len();
        }
    }
    issues
}
