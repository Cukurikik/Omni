// Omni LoRI Orthogonal Regularization (Rust)
// Ref: juzhengz/LoRI — COLM'25
pub fn orthogonal_reg_loss(a: &[Vec<f64>], lambda: f64) -> f64 {
    let r = a.len(); if r == 0 { return 0.0; }
    let d = a[0].len();
    let mut loss = 0.0;
    for i in 0..r {
        for j in 0..r {
            let dot: f64 = (0..d).map(|k| a[i][k] * a[j][k]).sum();
            let target = if i == j { 1.0 } else { 0.0 };
            loss += (dot - target).powi(2);
        }
    }
    lambda * loss
}
pub fn task_interference(deltas: &[Vec<f64>]) -> f64 {
    if deltas.len() < 2 { return 0.0; }
    let mut total = 0.0; let mut pairs = 0;
    for i in 0..deltas.len() {
        for j in (i+1)..deltas.len() {
            let dot: f64 = deltas[i].iter().zip(&deltas[j]).map(|(a,b)| a*b).sum();
            let ni: f64 = deltas[i].iter().map(|x| x*x).sum::<f64>().sqrt().max(1e-8);
            let nj: f64 = deltas[j].iter().map(|x| x*x).sum::<f64>().sqrt().max(1e-8);
            total += (dot / (ni * nj)).abs(); pairs += 1;
        }
    }
    total / pairs as f64
}
