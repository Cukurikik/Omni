use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, PartialEq)]
pub enum RateLimitError {
    RateLimitExceeded,
    SystemClockError,
}

struct TokenBucket {
    tokens: f64,
    last_refill: u64,
}

/// Omni Mother System - Security Layer
/// Thread-safe IP-based Token Bucket Rate Limiter
pub struct IpRateLimitFilter {
    buckets: Arc<Mutex<HashMap<String, TokenBucket>>>,
    capacity: f64,
    refill_rate_per_sec: f64,
}

impl IpRateLimitFilter {
    pub fn new(capacity: f64, refill_rate_per_sec: f64) -> Self {
        Self {
            buckets: Arc::new(Mutex::new(HashMap::new())),
            capacity,
            refill_rate_per_sec,
        }
    }

    fn current_time_sec() -> Result<u64, RateLimitError> {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs())
            .map_err(|_| RateLimitError::SystemClockError)
    }

    /// Checks if a request from the given IP is allowed.
    /// Strict adherence to monadic Result patterns.
    pub fn check_request(&self, ip_address: &str) -> Result<bool, RateLimitError> {
        let now = Self::current_time_sec()?;
        
        let mut map = self.buckets.lock().unwrap(); // Standard mutex is acceptable here; in extreme load, use RwLock or concurrent map.

        let bucket = map.entry(ip_address.to_string()).or_insert(TokenBucket {
            tokens: self.capacity,
            last_refill: now,
        });

        // Refill tokens
        if now > bucket.last_refill {
            let delta = (now - bucket.last_refill) as f64;
            bucket.tokens = f64::min(self.capacity, bucket.tokens + (delta * self.refill_rate_per_sec));
            bucket.last_refill = now;
        }

        // Consume token
        if bucket.tokens >= 1.0 {
            bucket.tokens -= 1.0;
            Ok(true) // Allowed
        } else {
            Err(RateLimitError::RateLimitExceeded) // Denied
        }
    }

    /// Periodically cleans up old IPs to prevent OOM vulnerabilities.
    /// To be called by a background concurrency worker.
    pub fn garbage_collect(&self, max_idle_sec: u64) -> Result<usize, RateLimitError> {
        let now = Self::current_time_sec()?;
        let mut map = self.buckets.lock().unwrap();
        
        let original_size = map.len();
        map.retain(|_, bucket| (now - bucket.last_refill) < max_idle_sec);
        
        Ok(original_size - map.len())
    }
}
