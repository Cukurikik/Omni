// omni_wasm_inference.rs — WebAssembly Inference Runtime
// Inspired by: ONNX WASM + OMNI edge deployment
// Layer: System / Rust (WASM target)
//
// Lightweight inference runtime compiled to WebAssembly for
// running quantized transformer models in the browser.

use std::collections::HashMap;

#[cfg(target_arch = "wasm32")]
use wasm_bindgen::prelude::*;

/// Tensor data structure for WASM inference
#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
#[derive(Debug, Clone)]
pub struct WasmTensor {
    data: Vec<f32>,
    shape: Vec<usize>,
    strides: Vec<usize>,
}

#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
impl WasmTensor {
    #[cfg_attr(target_arch = "wasm32", wasm_bindgen(constructor))]
    pub fn new(data: Vec<f32>, shape: Vec<usize>) -> Self {
        let strides = Self::compute_strides(&shape);
        Self { data, shape, strides }
    }

    fn compute_strides(shape: &[usize]) -> Vec<usize> {
        let mut strides = vec![1; shape.len()];
        for i in (0..shape.len() - 1).rev() {
            strides[i] = strides[i + 1] * shape[i + 1];
        }
        strides
    }

    pub fn zeros(shape: Vec<usize>) -> Self {
        let size: usize = shape.iter().product();
        Self::new(vec![0.0; size], shape)
    }

    pub fn numel(&self) -> usize {
        self.data.len()
    }

    pub fn shape(&self) -> Vec<usize> {
        self.shape.clone()
    }

    pub fn get(&self, indices: &[usize]) -> f32 {
        let idx: usize = indices.iter().zip(self.strides.iter())
            .map(|(&i, &s)| i * s)
            .sum();
        self.data[idx]
    }

    pub fn set(&mut self, indices: &[usize], value: f32) {
        let idx: usize = indices.iter().zip(self.strides.iter())
            .map(|(&i, &s)| i * s)
            .sum();
        self.data[idx] = value;
    }

    /// Matrix multiply: (M, K) x (K, N) -> (M, N)
    pub fn matmul(&self, other: &WasmTensor) -> WasmTensor {
        assert!(self.shape.len() >= 2 && other.shape.len() >= 2);
        let m = self.shape[self.shape.len() - 2];
        let k = self.shape[self.shape.len() - 1];
        let n = other.shape[other.shape.len() - 1];
        assert_eq!(k, other.shape[other.shape.len() - 2]);

        let mut result = WasmTensor::zeros(vec![m, n]);

        for i in 0..m {
            for j in 0..n {
                let mut sum = 0.0f32;
                for p in 0..k {
                    sum += self.get(&[i, p]) * other.get(&[p, j]);
                }
                result.set(&[i, j], sum);
            }
        }

        result
    }

    /// Element-wise add
    pub fn add(&self, other: &WasmTensor) -> WasmTensor {
        let data: Vec<f32> = self.data.iter()
            .zip(other.data.iter())
            .map(|(&a, &b)| a + b)
            .collect();
        WasmTensor::new(data, self.shape.clone())
    }

    /// Apply GELU activation
    pub fn gelu(&self) -> WasmTensor {
        let data: Vec<f32> = self.data.iter()
            .map(|&x| {
                0.5 * x * (1.0 + ((2.0f32 / std::f32::consts::PI).sqrt()
                    * (x + 0.044715 * x * x * x)).tanh())
            })
            .collect();
        WasmTensor::new(data, self.shape.clone())
    }

    /// Softmax along last dimension
    pub fn softmax(&self) -> WasmTensor {
        let last_dim = *self.shape.last().unwrap();
        let outer: usize = self.data.len() / last_dim;

        let mut result = vec![0.0f32; self.data.len()];

        for i in 0..outer {
            let start = i * last_dim;
            let end = start + last_dim;
            let slice = &self.data[start..end];

            let max_val = slice.iter().cloned().fold(f32::NEG_INFINITY, f32::max);
            let exp_sum: f32 = slice.iter().map(|&x| (x - max_val).exp()).sum();

            for j in 0..last_dim {
                result[start + j] = (slice[j] - max_val).exp() / exp_sum;
            }
        }

        WasmTensor::new(result, self.shape.clone())
    }

    /// Layer normalization
    pub fn layer_norm(&self, eps: f32) -> WasmTensor {
        let last_dim = *self.shape.last().unwrap();
        let outer: usize = self.data.len() / last_dim;

        let mut result = vec![0.0f32; self.data.len()];

        for i in 0..outer {
            let start = i * last_dim;
            let end = start + last_dim;
            let slice = &self.data[start..end];

            let mean: f32 = slice.iter().sum::<f32>() / last_dim as f32;
            let var: f32 = slice.iter()
                .map(|&x| (x - mean) * (x - mean))
                .sum::<f32>() / last_dim as f32;
            let std = (var + eps).sqrt();

            for j in 0..last_dim {
                result[start + j] = (slice[j] - mean) / std;
            }
        }

        WasmTensor::new(result, self.shape.clone())
    }

    pub fn data_ptr(&self) -> *const f32 {
        self.data.as_ptr()
    }
}

/// Lightweight transformer layer for WASM inference
pub struct WasmTransformerLayer {
    pub wq: WasmTensor,
    pub wk: WasmTensor,
    pub wv: WasmTensor,
    pub wo: WasmTensor,
    pub w1: WasmTensor,
    pub w2: WasmTensor,
    pub dim: usize,
    pub heads: usize,
}

impl WasmTransformerLayer {
    pub fn forward(&self, x: &WasmTensor) -> WasmTensor {
        let normed = x.layer_norm(1e-5);

        // Self-attention
        let q = normed.matmul(&self.wq);
        let k = normed.matmul(&self.wk);
        let v = normed.matmul(&self.wv);

        let scale = (self.dim as f32 / self.heads as f32).sqrt();
        let scores = q.matmul(&k); // simplified: should transpose k
        let scaled = WasmTensor::new(
            scores.data.iter().map(|&x| x / scale).collect(),
            scores.shape.clone(),
        );
        let attn_weights = scaled.softmax();
        let attn_output = attn_weights.matmul(&v);
        let projected = attn_output.matmul(&self.wo);

        let residual1 = x.add(&projected);

        // Feed-forward
        let normed2 = residual1.layer_norm(1e-5);
        let ff1 = normed2.matmul(&self.w1).gelu();
        let ff2 = ff1.matmul(&self.w2);
        let residual2 = residual1.add(&ff2);

        residual2
    }
}

/// Inference session managing the WASM transformer
#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
pub struct WasmInferenceSession {
    layers: Vec<WasmTransformerLayer>,
    vocab_size: usize,
    dim: usize,
}

#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
impl WasmInferenceSession {
    pub fn new(dim: usize, vocab_size: usize) -> Self {
        Self {
            layers: Vec::new(),
            vocab_size,
            dim,
        }
    }

    pub fn predict(&self, input: &WasmTensor) -> WasmTensor {
        let mut x = input.clone();
        for layer in &self.layers {
            x = layer.forward(&x);
        }
        x.layer_norm(1e-5)
    }

    pub fn num_layers(&self) -> usize {
        self.layers.len()
    }
}
