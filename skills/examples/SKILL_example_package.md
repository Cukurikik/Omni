# SKILL: CONTOH — Membuat Package dari Nol
**File:** `examples/SKILL_example_package.md`

---

## Tutorial: Membuat dan Mempublikasikan Package OMNI

Contoh ini membangun package `omni-currency-converter` — konversi mata uang real-time yang bisa digunakan developer lain.

---

### Langkah 1: Buat Project Baru

```bash
omni new omni-currency-converter
cd omni-currency-converter
```

Output struktur yang ter-generate:
```
omni-currency-converter/
├── Omnifile.toml          ← sudah diisi template
├── README.md              ← template kosong
├── CHANGELOG.md           ← template kosong
├── LICENSE                ← MIT by default
└── src/
    └── lib.omni           ← entry point kosong
```

---

### Langkah 2: Isi Omnifile.toml

```toml
[package]
name        = "omni-currency-converter"
version     = "1.0.0"
authors     = ["Nama Dev <dev@example.com>"]
description = "Konversi mata uang real-time untuk 170+ currencies dengan caching otomatis"
license     = "MIT"
keywords    = ["currency", "forex", "finance", "api"]
edition     = "omni-2025"

[dependencies]
omni-std = "^2.0"
omni-net = "^1.5"

[permissions]
allow_net = ["api.exchangerate-api.com", "open.er-api.com"]
allow_fs  = ["/tmp/currency-cache/"]
allow_env = ["EXCHANGE_API_KEY"]

[build]
target   = ["wasm32", "x86_64-linux", "aarch64-apple", "x86_64-windows"]
optimize = "release"

[publish]
registry  = "https://nexus.omniframework.dev"
tier      = "free"
price_usd = 0
```

---

### Langkah 3: Tulis Kode

```omni
// src/lib.omni — entry point publik

pub use domain::Currency;
pub use domain::ConversionResult;
pub use domain::CurrencyConverter;

pub fn init() -> Result<CurrencyConverter, InitError> {
  CurrencyConverter::new()
}
```

```omni
// src/domain/converter.cs — logika bisnis utama

/// Konverter mata uang dengan caching otomatis 1 jam.
///
/// @example
///   let conv = CurrencyConverter::new()?
///   let result = conv.convert(100.0, "USD", "IDR")?
///   println!("{} USD = {} IDR", result.amount, result.converted)
///
/// @since 1.0.0
/// @tags ["finance", "forex", "stable"]
cs::domain pub struct CurrencyConverter {
  cache: HashMap<String, ExchangeRate>,
  cache_expiry: DateTime,
}

impl CurrencyConverter {
  pub fn new() -> Result<Self, InitError> {
    Ok(Self {
      cache: HashMap::new(),
      cache_expiry: DateTime::now(),
    })
  }

  /// Mengkonversi jumlah dari satu mata uang ke mata uang lain.
  ///
  /// @param amount - Jumlah yang akan dikonversi
  /// @param from   - Kode mata uang asal (ISO 4217, contoh: "USD")
  /// @param to     - Kode mata uang tujuan (contoh: "IDR")
  /// @returns ConversionResult berisi nilai terkonversi dan rate yang digunakan
  pub fn convert(
    &mut self,
    amount: f64,
    from: &str,
    to: &str
  ) -> Result<ConversionResult, ConversionError> {
    let rate = self.get_rate(from, to)?
    Ok(ConversionResult {
      original_amount: amount,
      original_currency: from.to_string(),
      converted_amount: amount * rate.value,
      target_currency: to.to_string(),
      rate: rate.value,
      timestamp: rate.fetched_at,
    })
  }

  fn get_rate(&mut self, from: &str, to: &str) -> Result<ExchangeRate, ConversionError> {
    let key = format!("{}_{}", from, to)

    // Cek cache
    if let Some(rate) = self.cache.get(&key) {
      if DateTime::now() < self.cache_expiry {
        return Ok(rate.clone())
      }
    }

    // Fetch baru dari API
    let rate = network::fetch_exchange_rate(from, to)?
    self.cache.insert(key, rate.clone())
    self.cache_expiry = DateTime::now() + Duration::hours(1)
    Ok(rate)
  }
}
```

```omni
// src/network/exchange_api.go — HTTP client

/// Mengambil exchange rate dari API eksternal.
/// Otomatis retry 3x dengan exponential backoff.
go pub fn fetch_exchange_rate(
  from: &str,
  to: &str
) -> Result<ExchangeRate, NetworkError> {
  let api_key = go::env::var("EXCHANGE_API_KEY")
    .map_err(|_| NetworkError::MissingApiKey)?

  let url = format!(
    "https://api.exchangerate-api.com/v4/latest/{}",
    from
  )

  let response = go::http::get_with_retry(url, retries: 3)
    .map_err(NetworkError::HttpError)?

  let data = go::json::parse::<ExchangeRateResponse>(response.body)?

  let rate = data.rates.get(to)
    .ok_or(NetworkError::CurrencyNotFound(to.to_string()))?

  Ok(ExchangeRate {
    value: *rate,
    fetched_at: DateTime::now(),
  })
}
```

---

### Langkah 4: Tulis Tests

```omni
// tests/unit/test_converter.omni

#[test]
fn test_convert_usd_to_idr_returns_ok() {
  let mut conv = CurrencyConverter::new().unwrap()
  let result = conv.convert(100.0, "USD", "IDR")
  assert!(result.is_ok())
  assert!(result.unwrap().converted_amount > 0.0)
}

#[test]
fn test_convert_invalid_currency_returns_err() {
  let mut conv = CurrencyConverter::new().unwrap()
  let result = conv.convert(100.0, "INVALID", "IDR")
  assert!(result.is_err())
  assert_eq!(result.unwrap_err(), ConversionError::CurrencyNotFound)
}

#[test]
fn test_caching_uses_cached_rate() {
  let mut conv = CurrencyConverter::new().unwrap()
  let result1 = conv.convert(100.0, "USD", "IDR").unwrap()
  let result2 = conv.convert(200.0, "USD", "IDR").unwrap()
  // Rate harus sama karena dari cache
  assert_eq!(result1.rate, result2.rate)
}
```

---

### Langkah 5: Tambahkan Contoh Penggunaan

```omni
// examples/basic_usage.omni

fn main() -> Result<(), Box<dyn Error>> {
  // Inisialisasi converter
  let mut converter = omni_currency_converter::init()?

  // Konversi USD ke IDR
  let result = converter.convert(100.0, "USD", "IDR")?
  println!("{} {} = {:.2} {}",
    result.original_amount,
    result.original_currency,
    result.converted_amount,
    result.target_currency
  )
  // Output: 100 USD = 1,585,200.00 IDR

  // Batch conversion
  let currencies = ["EUR", "GBP", "JPY", "SGD"]
  for currency in currencies {
    let r = converter.convert(1.0, "USD", currency)?
    println!("1 USD = {:.4} {}", r.converted_amount, currency)
  }

  Ok(())
}
```

---

### Langkah 6: Build, Test, Publish

```bash
# Validasi kode
omni check --strict

# Jalankan semua test
omni test --all --coverage
# → Coverage: 91% ✓

# Generate dokumentasi
omni doc --format openapi --output docs/api/

# Build untuk semua platform
omni build --release --target all

# Dry run sebelum publish
omni publish --dry-run
# → Akan mengupload 23 file (47.2 KB) ke nexus.omniframework.dev ✓

# Publish!
omni publish
# → Package tersedia di: https://nexus.omniframework.dev/packages/omni-currency-converter

# Developer lain sekarang bisa install dengan:
# omni get omni-currency-converter
```

---

*ANTIGRAVITY Skills — examples/SKILL_example_package.md*
