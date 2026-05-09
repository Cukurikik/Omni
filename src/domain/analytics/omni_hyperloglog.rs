// omni_hyperloglog.rs — HyperLogLog Distinct Counter
// Layer: Domain / Analytics
// Inspired by: Redis Data Structures
//
// Implements the HyperLogLog algorithm for estimating the cardinality 
// (number of distinct elements) of extremely large datasets using only 
// a few kilobytes of memory and a single pass. Zero mock.

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

pub struct OmniHyperLogLog {
    registers: Vec<u8>,
    num_registers: usize,
    b: u32,
    alpha: f64,
}

impl OmniHyperLogLog {
    /// Creates a new HLL instance. `b` determines the number of registers (2^b).
    /// Standard is b=14 (16384 registers, ~12KB memory)
    pub fn new(b: u32) -> Self {
        assert!(b >= 4 && b <= 16, "b must be between 4 and 16");
        let num_registers = 1 << b;
        
        // Alpha constant bias correction based on number of registers
        let alpha = match num_registers {
            16 => 0.673,
            32 => 0.697,
            64 => 0.709,
            m => 0.7213 / (1.0 + 1.079 / (m as f64)),
        };

        OmniHyperLogLog {
            registers: vec![0; num_registers],
            num_registers,
            b,
            alpha,
        }
    }

    /// Add an element to the HLL.
    pub fn add<T: Hash>(&mut self, item: &T) {
        let mut hasher = DefaultHasher::new();
        item.hash(&mut hasher);
        let hash = hasher.finish();

        // Use top 'b' bits for register index
        let index = (hash >> (64 - self.b)) as usize;
        
        // Count leading zeros in the remaining bits
        let w = (hash << self.b) >> self.b; // Clear top b bits
        let rho = if w == 0 {
            65 - self.b as u8
        } else {
            w.leading_zeros() as u8 + 1
        };

        // Update register if new leading zero count is greater
        if rho > self.registers[index] {
            self.registers[index] = rho;
        }
    }

    /// Estimates the cardinality of the added elements.
    pub fn count(&self) -> f64 {
        let mut harmonic_mean_sum = 0.0;
        let mut zero_registers = 0;

        for &r in &self.registers {
            harmonic_mean_sum += 2.0_f64.powi(-(r as i32));
            if r == 0 {
                zero_registers += 1;
            }
        }

        let m = self.num_registers as f64;
        let mut estimate = self.alpha * m * m / harmonic_mean_sum;

        // Linear counting correction for small estimates
        if estimate <= 2.5 * m {
            if zero_registers > 0 {
                estimate = m * (m / zero_registers as f64).ln();
            }
        } 
        // Large range correction (rare for 64-bit hashes, but standard HLL)
        else if estimate > (1.0 / 30.0) * 2.0_f64.powi(64) {
            estimate = -2.0_f64.powi(64) * (1.0 - estimate / 2.0_f64.powi(64)).ln();
        }

        estimate
    }
}
