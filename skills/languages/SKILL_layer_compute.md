# SKILL: COMPUTE LAYER — Python, Julia, R
**File:** `languages/SKILL_layer_compute.md`  
**Layer:** Languages  
**Bahasa:** Python · Julia · R

---

## Peran Domain

Compute Layer menangani semua komputasi numerik, machine learning, data science, dan analisis statistik. Layer ini bekerja dengan data dalam jumlah besar dan harus dioptimasi untuk throughput.

| Bahasa | Keunggulan | Kapan Digunakan |
|--------|-----------|-----------------|
| **Python** | Ekosistem ML terlengkap, data wrangling, scripting | ML pipeline, preprocessing, AutoML |
| **Julia** | SIMD native, kecepatan mendekati C, HPC | Training loop, numerical solver, HFT algo |
| **R** | Statistical inference, distribusi probabilitas | Risk analysis, A/B testing, financial modeling |

---

## Python — Idiom OMNI

```omni
// ML fraud detection pipeline
py:: fn build_fraud_detector(
  training_data: DataFrame
) -> Result<FraudModel, MLError> {

  let features = py::pandas::DataFrame::from(training_data)
    .dropna()
    .select(["amount", "merchant_category", "hour_of_day", "velocity"])

  let X = features.drop("is_fraud")
  let y = features["is_fraud"]

  let model = py::sklearn::ensemble::GradientBoostingClassifier {
    n_estimators: 200,
    max_depth: 5,
    learning_rate: 0.05,
  }

  model.fit(X, y)?
  Ok(FraudModel::from(model))
}
```

---

## Julia — Idiom OMNI (SIMD + HPC)

```omni
// SIMD-accelerated price computation untuk HFT
@julia_simd fn compute_vwap(
  prices: Vec<f64>,
  volumes: Vec<f64>
) -> f64 {
  // Julia otomatis vektorisasi loop ini ke instruksi AVX-512
  let weighted_sum = prices.iter().zip(volumes.iter())
    .map(|(p, v)| p * v)
    .sum::<f64>()

  let total_volume = volumes.iter().sum::<f64>()
  weighted_sum / total_volume
}

// Numerical ODE solver untuk option pricing (Black-Scholes)
@julia_simd fn black_scholes_call(
  S: f64, K: f64, r: f64, sigma: f64, T: f64
) -> f64 {
  let d1 = (S / K).ln() + (r + 0.5 * sigma * sigma) * T / (sigma * T.sqrt())
  let d2 = d1 - sigma * T.sqrt()
  S * r::stat::norm_cdf(d1) - K * (-r * T).exp() * r::stat::norm_cdf(d2)
}
```

---

## R — Idiom OMNI (Statistical Analysis)

```omni
// Risk analysis dengan Value at Risk (VaR)
r::stat fn calculate_portfolio_var(
  returns: Vec<f64>,
  confidence_level: f64
) -> Result<VaRReport, StatError> {

  let mean   = r::stat::mean(&returns)
  let stddev = r::stat::sd(&returns)
  let var    = r::stat::qnorm(1.0 - confidence_level, mean, stddev)

  Ok(VaRReport {
    var_95:     var,
    cvar_95:    r::stat::expected_shortfall(&returns, confidence_level),
    sharpe:     mean / stddev * 252.0_f64.sqrt(),
    max_drawdown: r::stat::max_drawdown(&returns),
  })
}
```

---

## Integrasi Lintas Compute Language

```omni
// Pipeline: Python preprocessing → Julia training → R evaluation
fn full_ml_pipeline(raw_data: RawDataset) -> Result<ModelReport, PipelineError> {
  let features = py::preprocess(raw_data)?          // Python untuk cleaning
  let model    = julia::train_model(features)?       // Julia untuk speed
  let report   = r::evaluate_model(model, features)? // R untuk statistik
  Ok(report)
}
```

---

## Aturan Compute Layer

1. Julia SIMD HARUS digunakan untuk semua loop numerik yang dieksekusi lebih dari 10.000 kali
2. Python dataframe DILARANG dimuat seluruhnya ke memori jika lebih dari 1GB — gunakan chunked loading
3. R hanya untuk analisis statistik — jangan gunakan R untuk HTTP request atau I/O
4. Semua model ML HARUS disimpan dalam format yang bisa di-load ulang tanpa retraining

---

*ANTIGRAVITY Skills — languages/SKILL_layer_compute.md*
