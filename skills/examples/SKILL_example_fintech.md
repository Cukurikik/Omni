# SKILL: CONTOH — Payment Gateway Fintech
**File:** `examples/SKILL_example_fintech.md`

---

## Studi Kasus: Payment Gateway Enterprise

### Struktur Project

```
payment-gateway/
├── Omnifile.toml
├── src/
│   ├── lib.omni
│   ├── system/
│   │   └── crypto.rs            ← Rust: enkripsi AES-256-GCM
│   ├── network/
│   │   ├── http_server.go       ← Go: HTTP/3 API server
│   │   └── webhook_handler.js   ← JS: webhook event streaming
│   ├── domain/
│   │   ├── schema.graphql       ← GraphQL: API contract
│   │   ├── payment.cs           ← C#: business logic + DDD
│   │   └── routes.rb            ← Ruby: REST routing
│   ├── compute/
│   │   └── fraud_detect.py      ← Python: ML fraud detection
│   └── ui/
│       └── dashboard.tsx        ← TypeScript: merchant dashboard
└── tests/
    ├── unit/
    └── integration/
```

### Omnifile.toml

```toml
[package]
name    = "enterprise-payment-gateway"
version = "2.0.0"
edition = "omni-2025"

[dependencies]
omni-std    = "^2.0"
omni-crypto = "^3.0"
omni-net    = "^1.5"
omni-db     = "^2.1"
omni-ml     = { version = "^1.0", features = ["fraud-detection"] }

[permissions]
allow_net = ["api.stripe.com", "api.midtrans.com", "api.xendit.co"]
allow_fs  = ["/tmp/payment-gateway/"]
allow_env = ["STRIPE_KEY", "MIDTRANS_KEY", "DB_URL"]
allow_thread = true

[build]
target   = ["x86_64-linux", "aarch64-linux"]
optimize = "release"
lto      = "thin"
```

### Kode Inti — Enkripsi Kartu (Rust)

```omni
// src/system/crypto.rs
use rust::aes_gcm::{Aes256Gcm, Key, Nonce}

/// Mengenkripsi data kartu kredit dengan AES-256-GCM.
/// Data asli tidak pernah disimpan — hanya ciphertext.
///
/// @param card_data - Data kartu dalam format PAN
/// @returns EncryptedCard dengan ciphertext + nonce
/// @since 2.0.0
pub fn encrypt_card_data(card_data: CardData) -> Result<EncryptedCard, CryptoError> {
  let key = load_encryption_key()?
  let nonce = generate_secure_nonce()
  let cipher = Aes256Gcm::new(&key)

  let ciphertext = cipher.encrypt(&nonce, card_data.as_bytes())
    .map_err(|_| CryptoError::EncryptionFailed)?

  // Zero-fill original data setelah enkripsi
  unsafe { c::memset(card_data.as_mut_ptr(), 0, card_data.len()) }

  Ok(EncryptedCard { ciphertext, nonce })
}
```

### Kode Inti — HTTP Server (Go)

```omni
// src/network/http_server.go
service PaymentApiServer {
  fn start(port: u16) -> Result<(), ServerError> {
    let router = go::http3::Router::new()

    // Route tanpa auth
    router.post("/v1/webhooks/stripe",  handle_stripe_webhook)

    // Route dengan auth middleware
    router.group("/v1", middleware: [authenticate, rate_limit]) {
      router.post("/payments",           create_payment)
      router.get("/payments/:id",        get_payment_status)
      router.post("/refunds",            create_refund)
    }

    go::http3::serve(format!("0.0.0.0:{}", port), router)
  }
}
```

### Kode Inti — Fraud Detection (Python)

```omni
// src/compute/fraud_detect.py
py:: class FraudDetector {
  model: py::sklearn::GradientBoostingClassifier
  threshold: f64

  fn predict(transaction: Transaction) -> Result<FraudScore, MLError> {
    let features = py::pandas::DataFrame::from_transaction(transaction)
    let proba = self.model.predict_proba(features)[0][1]  // probabilitas fraud

    Ok(FraudScore {
      score:      proba,
      is_fraud:   proba > self.threshold,
      confidence: if proba > 0.9 || proba < 0.1 { Confidence::High } else { Confidence::Low }
    })
  }
}
```

### Deploy

```bash
omni build --release --target x86_64-linux
omni unikernel build --target cloud
omni cloud deploy payment-gateway.ukl --region id-jkt-1
# → https://payment-gateway.omnicloud.dev (4.8MB unikernel, cold start 4ms)
```

---

# SKILL: CONTOH — AI Analytics Platform
**File:** `examples/SKILL_example_ai_platform.md`

---

## Studi Kasus: Platform Analitik AI

### Struktur Project

```
ai-analytics/
├── Omnifile.toml
├── src/
│   ├── system/
│   │   └── tensor_ops.cpp       ← C++: GPU tensor operations (CUDA)
│   ├── compute/
│   │   ├── training.jl          ← Julia: SIMD training loop
│   │   ├── stats.r              ← R: statistical evaluation
│   │   └── pipeline.py         ← Python: data preprocessing
│   ├── network/
│   │   └── streaming.js         ← JS: real-time WebSocket streaming
│   ├── domain/
│   │   ├── schema.graphql       ← GraphQL: API contract
│   │   └── reports.rb           ← Ruby: report generation DSL
│   └── ui/
│       └── dashboard.tsx        ← TypeScript: interactive charts
└── tests/
```

### Kode Inti — GPU Training (Julia SIMD)

```omni
// src/compute/training.jl
@julia_simd fn train_model_epoch(
  X: &Matrix<f32>,
  y: &Vector<f32>,
  weights: &mut Vector<f32>,
  learning_rate: f32
) -> f32 {  // returns loss

  // Forward pass — vektorisasi otomatis ke AVX-512
  let predictions = X.mul_vector(weights)
  let errors = predictions - y

  // Backward pass — gradient descent
  let gradients = X.transpose().mul_vector(&errors) / X.rows() as f32
  weights.sub_assign(&(gradients * learning_rate))

  // MSE loss
  errors.map(|e| e * e).sum() / errors.len() as f32
}
```

---

*ANTIGRAVITY Skills — examples*
