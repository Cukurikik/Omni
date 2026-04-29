use omni_sys::Result;

pub fn calculate_uncertainty(probs: Vec<f64>) -> Result<f64, &'static str> {
    if probs.is_empty() {
        return Err("Empty probabilities");
    }
    let entropy: f64 = probs.iter().map(|p| -p * p.log2()).sum();
    Ok(entropy)
}
