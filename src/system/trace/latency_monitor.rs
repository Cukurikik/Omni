use std::time::{Instant, Duration};

pub struct OmniResult<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

pub struct LatencyMonitor {
    pub threshold: Duration,
}

impl LatencyMonitor {
    pub fn monitor_execution<F, R>(&self, task: F) -> OmniResult<(R, Duration)> 
    where F: FnOnce() -> R {
        let start = Instant::now();
        let result = task();
        let elapsed = start.elapsed();
        
        if elapsed > self.threshold {
            return OmniResult { 
                value: Some((result, elapsed)), 
                error: Some(format!("Latency exceeded threshold: {:?}", elapsed)), 
                is_ok: false 
            };
        }
        
        OmniResult { value: Some((result, elapsed)), error: None, is_ok: true }
    }
}
