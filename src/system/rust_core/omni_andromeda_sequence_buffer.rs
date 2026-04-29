// Omni Andromeda Sequence Buffer (Rust)
// System Layer: Memory-safe ring buffer for ultra-long sequences (100K+).
// Ref: kyegomez/Andromeda — 100K+ token processing.

pub struct SequenceRingBuffer { data: Vec<f32>, head: usize, capacity: usize }
impl SequenceRingBuffer {
    pub fn new(cap: usize) -> Self { Self { data: vec![0.0; cap], head: 0, capacity: cap } }
    pub fn push(&mut self, val: f32) { self.data[self.head % self.capacity] = val; self.head += 1; }
    pub fn len(&self) -> usize { self.head.min(self.capacity) }
    pub fn get(&self, idx: usize) -> Option<f32> {
        if idx >= self.len() { return None; }
        let real = if self.head <= self.capacity { idx } else { (self.head - self.capacity + idx) % self.capacity };
        Some(self.data[real])
    }
}
