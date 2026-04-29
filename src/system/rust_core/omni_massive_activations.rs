// Omni Massive Activations Detector (Rust)
// Ref: locuslab/massive-activations — MIT
pub fn detect_massive(activations: &[f64], threshold_std: f64) -> Vec<usize> {
    let n = activations.len() as f64;
    if n == 0.0 { return vec![]; }
    let mean = activations.iter().sum::<f64>() / n;
    let var = activations.iter().map(|a| (a - mean).powi(2)).sum::<f64>() / n;
    let std = var.sqrt().max(1e-8);
    let thresh = mean + threshold_std * std;
    activations.iter().enumerate().filter(|(_, &a)| a.abs() > thresh).map(|(i, _)| i).collect()
}
pub fn kurtosis(activations: &[f64]) -> f64 {
    let n = activations.len() as f64;
    if n < 4.0 { return 0.0; }
    let mean = activations.iter().sum::<f64>() / n;
    let std = (activations.iter().map(|a| (a-mean).powi(2)).sum::<f64>() / n).sqrt().max(1e-8);
    activations.iter().map(|a| ((a-mean)/std).powi(4)).sum::<f64>() / n - 3.0
}
