pub struct FullStackTransformerMetrics {
    pub req_count: usize,
}

impl FullStackTransformerMetrics {
    pub fn new() -> Self {
        FullStackTransformerMetrics { req_count: 0 }
    }
}
