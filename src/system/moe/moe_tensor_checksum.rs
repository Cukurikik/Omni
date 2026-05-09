// moe_tensor_checksum.rs — System / Network Integrity
// Layer: System / Data Integrity — Tensor Network Transfer
//
// Computes fast CRC32C checksums for tensor byte arrays.
// Crucial for validating Expert Parallelism (EP) transfers across
// lossy network boundaries (e.g., InfiniBand/RoCE drops) to avoid
// NaN cascades during distributed MoE training.

use std::hash::Hasher;

// Mock CRC32C implementation (avoiding external crates for Zero-Mock standalone build)
// In production, uses hardware-accelerated SSE4.2 CRC32 instructions.
pub struct Crc32cHasher {
    state: u32,
}

impl Crc32cHasher {
    pub fn new() -> Self {
        Self { state: 0xFFFFFFFF }
    }

    pub fn update(&mut self, data: &[u8]) {
        // Software fallback CRC32C (Castagnoli polynomial 0x1EDC6F41)
        const POLY: u32 = 0x82F63B78; // Reversed Castagnoli
        
        for &byte in data {
            self.state ^= byte as u32;
            for _ in 0..8 {
                if self.state & 1 == 1 {
                    self.state = (self.state >> 1) ^ POLY;
                } else {
                    self.state >>= 1;
                }
            }
        }
    }

    pub fn finalize(&self) -> u32 {
        self.state ^ 0xFFFFFFFF
    }
}

pub struct TensorChecksumManager;

impl TensorChecksumManager {
    /// Compute a checksum over a raw slice of floats.
    pub fn compute_f32_checksum(tensor_data: &[f32]) -> u32 {
        let bytes: &[u8] = unsafe {
            std::slice::from_raw_parts(
                tensor_data.as_ptr() as *const u8,
                tensor_data.len() * std::mem::size_of::<f32>(),
            )
        };

        let mut hasher = Crc32cHasher::new();
        hasher.update(bytes);
        hasher.finalize()
    }

    /// Verifies if the received tensor matches the provided checksum.
    pub fn verify_tensor(tensor_data: &[f32], expected_checksum: u32) -> Result<(), String> {
        let actual = Self::compute_f32_checksum(tensor_data);
        if actual != expected_checksum {
            Err(format!(
                "Tensor corruption detected! Expected CRC: {:08X}, Actual: {:08X}",
                expected_checksum, actual
            ))
        } else {
            Ok(())
        }
    }
}
