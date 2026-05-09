use std::collections::HashMap;

pub struct SRLGraphBuilder {
    nodes: HashMap<usize, String>,
    edges: Vec<(usize, usize, String)>,
}

impl SRLGraphBuilder {
    pub fn new() -> Self {
        SRLGraphBuilder {
            nodes: HashMap::new(),
            edges: Vec::new(),
        }
    }

    pub fn add_predicate(&mut self, id: usize, token: String) -> Result<(), String> {
        self.nodes.insert(id, token);
        Ok(())
    }

    pub fn add_argument(&mut self, pred_id: usize, arg_id: usize, role: String) -> Result<(), String> {
        if !self.nodes.contains_key(&pred_id) {
            return Err("Predicate not found".to_string());
        }
        self.edges.push((pred_id, arg_id, role));
        Ok(())
    }
}
