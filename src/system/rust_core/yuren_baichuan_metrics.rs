pub struct YurenBaichuanMetrics {
    pub tokens_processed: usize,
}

impl YurenBaichuanMetrics {
    pub fn new() -> Self {
        YurenBaichuanMetrics { tokens_processed: 0 }
    }
}
