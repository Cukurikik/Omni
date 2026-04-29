// Omni Q-GaLore INT4 Quantization Kernel (Rust)
// Ref: VITA-Group/Q-GaLore — Apache-2.0

pub struct Int4Packed { pub data: Vec<u8>, pub scale: f32, pub zero_point: f32, pub len: usize }

pub fn int4_quantize(values: &[f32]) -> Int4Packed {
    if values.is_empty() { return Int4Packed { data: vec![], scale: 1.0, zero_point: 0.0, len: 0 }; }
    let vmin = values.iter().cloned().fold(f32::INFINITY, f32::min);
    let vmax = values.iter().cloned().fold(f32::NEG_INFINITY, f32::max);
    let scale = if (vmax - vmin).abs() > f32::EPSILON { (vmax - vmin) / 15.0 } else { 1.0 };
    let quantized: Vec<u8> = values.iter().map(|v| ((v - vmin) / scale).round().max(0.0).min(15.0) as u8).collect();
    let mut packed = Vec::with_capacity((quantized.len() + 1) / 2);
    for chunk in quantized.chunks(2) {
        let high = chunk[0];
        let low = if chunk.len() > 1 { chunk[1] } else { 0 };
        packed.push((high << 4) | (low & 0x0F));
    }
    Int4Packed { data: packed, scale, zero_point: vmin, len: values.len() }
}

pub fn int4_dequantize(packed: &Int4Packed) -> Vec<f32> {
    let mut result = Vec::with_capacity(packed.len);
    for (i, &byte) in packed.data.iter().enumerate() {
        let high = (byte >> 4) as f32;
        result.push(high * packed.scale + packed.zero_point);
        if result.len() < packed.len {
            let low = (byte & 0x0F) as f32;
            result.push(low * packed.scale + packed.zero_point);
        }
    }
    result
}
