pub struct DocSumMetrics {
    pub docs_summarized: usize,
}

impl DocSumMetrics {
    pub fn new() -> Self {
        DocSumMetrics { docs_summarized: 0 }
    }
}
