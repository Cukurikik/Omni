// omni_model_quantizer.rs — Model Weight Quantization Engine
// Inspired by: GPTQ/AWQ weight quantization for deployment
// Layer: System / Rust
//
// Post-training quantization of transformer weights from
// fp32/fp16 to int8/int4 for efficient inference deployment.

use std::collections::HashMap;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum QuantizationType {
    Int8Symmetric,
    Int8Asymmetric,
    Int4Symmetric,
    Int4Grouped,
    NF4,  // NormalFloat4
}

#[derive(Debug, Clone)]
pub struct QuantizationConfig {
    pub quant_type: QuantizationType,
    pub group_size: usize,
    pub calibration_samples: usize,
    pub per_channel: bool,
    pub exclude_layers: Vec<String>,
}

impl Default for QuantizationConfig {
    fn default() -> Self {
        Self {
            quant_type: QuantizationType::Int8Symmetric,
            group_size: 128,
            calibration_samples: 256,
            per_channel: true,
            exclude_layers: vec!["lm_head".to_string(), "embed_tokens".to_string()],
        }
    }
}

#[derive(Debug, Clone)]
pub struct QuantizedTensor {
    pub data: Vec<i8>,
    pub scale: Vec<f32>,
    pub zero_point: Vec<i32>,
    pub shape: Vec<usize>,
    pub quant_type: QuantizationType,
    pub group_size: usize,
    pub original_dtype_bytes: usize,
}

impl QuantizedTensor {
    pub fn compression_ratio(&self) -> f64 {
        let original_bytes = self.shape.iter().product::<usize>() * self.original_dtype_bytes;
        let quantized_bytes = self.data.len() + self.scale.len() * 4 + self.zero_point.len() * 4;
        original_bytes as f64 / quantized_bytes as f64
    }

    pub fn dequantize(&self) -> Vec<f32> {
        match self.quant_type {
            QuantizationType::Int8Symmetric => self.dequantize_int8_symmetric(),
            QuantizationType::Int8Asymmetric => self.dequantize_int8_asymmetric(),
            QuantizationType::Int4Symmetric => self.dequantize_int4_symmetric(),
            _ => self.dequantize_int8_symmetric(),
        }
    }

    fn dequantize_int8_symmetric(&self) -> Vec<f32> {
        let total = self.shape.iter().product::<usize>();
        let mut output = Vec::with_capacity(total);

        if self.scale.len() == 1 {
            // Per-tensor quantization
            let s = self.scale[0];
            for &val in &self.data {
                output.push(val as f32 * s);
            }
        } else {
            // Per-channel or per-group
            let elements_per_scale = total / self.scale.len();
            for (group_idx, &s) in self.scale.iter().enumerate() {
                let start = group_idx * elements_per_scale;
                let end = std::cmp::min(start + elements_per_scale, self.data.len());
                for i in start..end {
                    output.push(self.data[i] as f32 * s);
                }
            }
        }

        output
    }

    fn dequantize_int8_asymmetric(&self) -> Vec<f32> {
        let total = self.shape.iter().product::<usize>();
        let mut output = Vec::with_capacity(total);
        let elements_per_group = if self.scale.len() > 0 { total / self.scale.len() } else { total };

        for (group_idx, (&s, &zp)) in self.scale.iter().zip(self.zero_point.iter()).enumerate() {
            let start = group_idx * elements_per_group;
            let end = std::cmp::min(start + elements_per_group, self.data.len());
            for i in start..end {
                output.push((self.data[i] as i32 - zp) as f32 * s);
            }
        }

        output
    }

    fn dequantize_int4_symmetric(&self) -> Vec<f32> {
        let total = self.shape.iter().product::<usize>();
        let mut output = Vec::with_capacity(total);
        let elements_per_scale = if self.scale.len() > 0 { total / self.scale.len() } else { total };

        for (group_idx, &s) in self.scale.iter().enumerate() {
            let start = group_idx * elements_per_scale;
            let end = std::cmp::min(start + elements_per_scale, total);
            for i in start..end {
                // Extract 4-bit value from packed int8
                let byte_idx = i / 2;
                let val = if byte_idx < self.data.len() {
                    if i % 2 == 0 {
                        (self.data[byte_idx] & 0x0F) as i8 - 8
                    } else {
                        ((self.data[byte_idx] >> 4) & 0x0F) as i8 - 8
                    }
                } else {
                    0
                };
                output.push(val as f32 * s);
            }
        }

        output
    }
}

pub struct OmniModelQuantizer {
    config: QuantizationConfig,
}

impl OmniModelQuantizer {
    pub fn new(config: QuantizationConfig) -> Self {
        Self { config }
    }

    /// Quantize a weight tensor to int8 symmetric
    pub fn quantize_int8_symmetric(&self, weights: &[f32], shape: &[usize]) -> QuantizedTensor {
        let total = weights.len();

        if self.config.per_channel && shape.len() >= 2 {
            let out_channels = shape[0];
            let elements_per_channel = total / out_channels;

            let mut data = vec![0i8; total];
            let mut scales = Vec::with_capacity(out_channels);

            for ch in 0..out_channels {
                let start = ch * elements_per_channel;
                let end = start + elements_per_channel;
                let channel_weights = &weights[start..end];

                let abs_max = channel_weights.iter()
                    .map(|w| w.abs())
                    .fold(0.0f32, f32::max)
                    .max(1e-10);

                let scale = abs_max / 127.0;
                scales.push(scale);

                for (i, &w) in channel_weights.iter().enumerate() {
                    let quantized = (w / scale).round().clamp(-127.0, 127.0) as i8;
                    data[start + i] = quantized;
                }
            }

            QuantizedTensor {
                data,
                scale: scales,
                zero_point: vec![0; out_channels],
                shape: shape.to_vec(),
                quant_type: QuantizationType::Int8Symmetric,
                group_size: elements_per_channel,
                original_dtype_bytes: 4,
            }
        } else {
            // Per-tensor quantization
            let abs_max = weights.iter()
                .map(|w| w.abs())
                .fold(0.0f32, f32::max)
                .max(1e-10);

            let scale = abs_max / 127.0;
            let data: Vec<i8> = weights.iter()
                .map(|&w| (w / scale).round().clamp(-127.0, 127.0) as i8)
                .collect();

            QuantizedTensor {
                data,
                scale: vec![scale],
                zero_point: vec![0],
                shape: shape.to_vec(),
                quant_type: QuantizationType::Int8Symmetric,
                group_size: total,
                original_dtype_bytes: 4,
            }
        }
    }

    /// Quantize a weight tensor to int8 asymmetric (min-max)
    pub fn quantize_int8_asymmetric(&self, weights: &[f32], shape: &[usize]) -> QuantizedTensor {
        let total = weights.len();
        let min_val = weights.iter().cloned().fold(f32::INFINITY, f32::min);
        let max_val = weights.iter().cloned().fold(f32::NEG_INFINITY, f32::max);

        let range = (max_val - min_val).max(1e-10);
        let scale = range / 255.0;
        let zero_point = (-min_val / scale).round() as i32;

        let data: Vec<i8> = weights.iter()
            .map(|&w| ((w / scale).round() as i32 + zero_point).clamp(0, 255) as i8)
            .collect();

        QuantizedTensor {
            data,
            scale: vec![scale],
            zero_point: vec![zero_point],
            shape: shape.to_vec(),
            quant_type: QuantizationType::Int8Asymmetric,
            group_size: total,
            original_dtype_bytes: 4,
        }
    }

    /// Compute quantization error (MSE)
    pub fn compute_error(original: &[f32], quantized: &QuantizedTensor) -> f64 {
        let dequantized = quantized.dequantize();
        if original.len() != dequantized.len() {
            return f64::INFINITY;
        }

        let mse: f64 = original.iter()
            .zip(dequantized.iter())
            .map(|(&a, &b)| ((a - b) as f64).powi(2))
            .sum::<f64>() / original.len() as f64;

        mse
    }
}

#[derive(Debug)]
pub struct QuantizationReport {
    pub total_params: usize,
    pub quantized_params: usize,
    pub excluded_params: usize,
    pub original_size_mb: f64,
    pub quantized_size_mb: f64,
    pub compression_ratio: f64,
    pub avg_mse: f64,
    pub layer_reports: HashMap<String, f64>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_int8_symmetric_roundtrip() {
        let config = QuantizationConfig::default();
        let quantizer = OmniModelQuantizer::new(config);

        let weights: Vec<f32> = (0..256).map(|i| (i as f32 - 128.0) / 128.0).collect();
        let shape = vec![16, 16];

        let quantized = quantizer.quantize_int8_symmetric(&weights, &shape);
        let mse = OmniModelQuantizer::compute_error(&weights, &quantized);

        assert!(mse < 0.001, "Quantization MSE too high: {}", mse);
        assert!(quantized.compression_ratio() > 2.0);
    }

    #[test]
    fn test_asymmetric_quantization() {
        let config = QuantizationConfig::default();
        let quantizer = OmniModelQuantizer::new(config);

        let weights: Vec<f32> = (0..100).map(|i| i as f32 * 0.01).collect();
        let shape = vec![10, 10];

        let quantized = quantizer.quantize_int8_asymmetric(&weights, &shape);
        let dequantized = quantized.dequantize();

        assert_eq!(dequantized.len(), weights.len());
    }
}
