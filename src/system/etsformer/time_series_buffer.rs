/// @omni-layer System | @omni-source dmlc/torchblocks + lucidrains/ETSformer-pytorch | @omni-lang Rust
/// @omni-description Time series buffer: lock-free circular buffer for
/// streaming time series data with windowed aggregation.
use std::sync::atomic::{AtomicUsize, Ordering};

#[derive(Debug)]
pub enum BufferError { Empty, Full }
pub type OmniResult<T> = Result<T, BufferError>;

pub struct TimeSeriesBuffer {
    data: Vec<f64>,
    capacity: usize,
    write_pos: AtomicUsize,
    count: AtomicUsize,
}

impl TimeSeriesBuffer {
    pub fn new(capacity: usize) -> Self {
        Self {
            data: vec![0.0; capacity],
            capacity,
            write_pos: AtomicUsize::new(0),
            count: AtomicUsize::new(0),
        }
    }

    pub fn push(&mut self, value: f64) -> OmniResult<usize> {
        let pos = self.write_pos.load(Ordering::Relaxed);
        self.data[pos] = value;
        self.write_pos.store((pos + 1) % self.capacity, Ordering::Relaxed);
        let c = self.count.fetch_add(1, Ordering::Relaxed);
        Ok(c.min(self.capacity - 1) + 1)
    }

    pub fn window(&self, size: usize) -> OmniResult<Vec<f64>> {
        let count = self.count.load(Ordering::Relaxed).min(self.capacity);
        let n = size.min(count);
        if n == 0 { return Err(BufferError::Empty); }
        let write = self.write_pos.load(Ordering::Relaxed);
        let mut result = Vec::with_capacity(n);
        for i in 0..n {
            let idx = (write + self.capacity - n + i) % self.capacity;
            result.push(self.data[idx]);
        }
        Ok(result)
    }

    pub fn moving_average(&self, window_size: usize) -> OmniResult<f64> {
        let w = self.window(window_size)?;
        Ok(w.iter().sum::<f64>() / w.len() as f64)
    }

    pub fn moving_std(&self, window_size: usize) -> OmniResult<f64> {
        let w = self.window(window_size)?;
        let mean = w.iter().sum::<f64>() / w.len() as f64;
        let var = w.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / w.len() as f64;
        Ok(var.sqrt())
    }

    pub fn exponential_smooth(&self, window_size: usize, alpha: f64) -> OmniResult<f64> {
        let w = self.window(window_size)?;
        let mut smoothed = w[0];
        for v in &w[1..] {
            smoothed = alpha * v + (1.0 - alpha) * smoothed;
        }
        Ok(smoothed)
    }

    pub fn len(&self) -> usize { self.count.load(Ordering::Relaxed).min(self.capacity) }
    pub fn capacity(&self) -> usize { self.capacity }
}
