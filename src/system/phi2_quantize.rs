use omni_sys::Result;

pub fn quantize_phi2(weights: Vec<f32>) -> Result<Vec<u8>, &'static str> {
    if weights.is_empty() {
        return Err("No weights");
    }
    Ok(weights.iter().map(|&w| (w * 255.0) as u8).collect())
}
