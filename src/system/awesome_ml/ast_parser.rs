pub struct AstNode {
    pub node_type: String,
    pub value: Option<String>,
    pub children: Vec<AstNode>,
}

impl AstNode {
    pub fn new(node_type: &str) -> Self {
        AstNode {
            node_type: node_type.to_string(),
            value: None,
            children: Vec::new(),
        }
    }

    pub fn extract_paths(&self, max_length: usize) -> Vec<String> {
        // Simulated AST path extraction for Code2Vec ML models
        let mut paths = Vec::new();
        if self.children.is_empty() {
            paths.push(self.node_type.clone());
        } else {
            for child in &self.children {
                paths.push(format!("{}->{}", self.node_type, child.node_type));
            }
        }
        paths
    }
}
