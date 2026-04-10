use std::collections::HashMap;

type OMNIfn = fn() -> String;

pub struct RadixNode {
    pub path: String,
    pub is_end: bool,
    pub handler: Option<OMNIfn>,
    pub children: HashMap<String, Box<RadixNode>>,
}

impl RadixNode {
    pub fn new(path: &str) -> Self {
        Self {
            path: path.to_string(),
            is_end: false,
            handler: None,
            children: HashMap::new(),
        }
    }
}

pub struct OmniRouter {
    pub root: RadixNode,
}

impl OmniRouter {
    pub fn new() -> Self {
        Self {
            root: RadixNode::new("/"),
        }
    }
    
    pub fn insert(&mut self, path: &str, handler: OMNIfn) {
        let mut current = &mut self.root;
        let segments: Vec<&str> = path.split('/').filter(|s| !s.is_empty()).collect();
        
        for seg in segments {
            current = current.children.entry(seg.to_string()).or_insert_with(|| Box::new(RadixNode::new(seg)));
        }
        current.is_end = true;
        current.handler = Some(handler);
    }
    
    pub fn route(&self, path: &str) -> Option<OMNIfn> {
        let mut current = &self.root;
        let segments: Vec<&str> = path.split('/').filter(|s| !s.is_empty()).collect();
        
        for seg in segments {
            if let Some(child) = current.children.get(seg) {
                current = child;
            } else {
                return None;
            }
        }
        
        if current.is_end {
            current.handler
        } else {
            None
        }
    }
}
