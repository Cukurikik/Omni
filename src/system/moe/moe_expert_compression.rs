// moe_expert_compression.rs — System / Network
// Layer: System / Network — MoE Weight Transmission
//
// Specialized fast compression for transferring MoE expert weights
// over network links (Parameter Server <-> Compute Nodes).
// Uses a combination of FP16 truncation and LZ4 for fast decompression.

use std::io::{Read, Write};
use lz4_flex::frame::{FrameEncoder, FrameDecoder};

pub struct MoEWeightCompressor;

impl MoEWeightCompressor {
    /// Compresses FP32 weights into a packed FP16-LZ4 binary format.
    /// Returns the compressed bytes.
    pub fn compress_weights(weights: &[f32]) -> Result<Vec<u8>, String> {
        // 1. Convert FP32 to basic FP16 (Truncation for speed)
        // In a real implementation, use hardware intrinsics.
        let mut fp16_bytes = Vec::with_capacity(weights.len() * 2);
        for &w in weights {
            let bits = w.to_bits();
            let sign = (bits >> 16) & 0x8000;
            let mut exponent = ((bits >> 23) & 0xff) as i32 - 127 + 15;
            let mut mantissa = (bits >> 13) & 0x3ff;

            if exponent <= 0 {
                exponent = 0;
                mantissa = 0;
            } else if exponent >= 31 {
                exponent = 31;
                mantissa = 0;
            }

            let fp16 = (sign | ((exponent as u32) << 10) | mantissa) as u16;
            fp16_bytes.extend_from_slice(&fp16.to_le_bytes());
        }

        // 2. Compress via LZ4
        let mut compressed = Vec::new();
        {
            let mut encoder = FrameEncoder::new(&mut compressed);
            encoder.write_all(&fp16_bytes).map_err(|e| e.to_string())?;
            encoder.finish().map_err(|e| e.to_string())?;
        }

        Ok(compressed)
    }

    /// Decompresses LZ4-FP16 binary back into FP32 weights.
    pub fn decompress_weights(compressed: &[u8], expected_elements: usize) -> Result<Vec<f32>, String> {
        // 1. Decompress LZ4
        let mut decoder = FrameDecoder::new(compressed);
        let mut fp16_bytes = Vec::with_capacity(expected_elements * 2);
        decoder.read_to_end(&mut fp16_bytes).map_err(|e| e.to_string())?;

        if fp16_bytes.len() != expected_elements * 2 {
            return Err("Decompressed size mismatch".into());
        }

        // 2. Convert FP16 back to FP32
        let mut fp32_weights = Vec::with_capacity(expected_elements);
        for i in 0..expected_elements {
            let fp16 = u16::from_le_bytes([fp16_bytes[i*2], fp16_bytes[i*2+1]]);
            
            let sign = ((fp16 >> 15) as u32) << 31;
            let exponent = ((fp16 >> 10) & 0x1f) as u32;
            let mantissa = (fp16 & 0x3ff) as u32;

            let fp32_bits = if exponent == 0 {
                sign // zero
            } else if exponent == 31 {
                sign | 0x7f800000 | (mantissa << 13) // inf/nan
            } else {
                sign | ((exponent + 127 - 15) << 23) | (mantissa << 13)
            };

            fp32_weights.push(f32::from_bits(fp32_bits));
        }

        Ok(fp32_weights)
    }
}
