# SKILL: ATURAN BESI PENULISAN KODE
**File:** `core/SKILL_rules.md`  
**Layer:** Core  
**Token Count:** ~600

---

## Aturan 1 — Monadic Error Handling (WAJIB MUTLAK)

Jangan pernah menggunakan `try/catch`. Semua fungsi yang bisa gagal HARUS mengembalikan `Result<T, E>`.

```omni
// SALAH — dilarang keras
try {
  processPayment()
} catch (e) {
  console.error(e)
}

// BENAR — wajib selalu
fn process_payment(req: PaymentRequest) -> Result<Receipt, PaymentError> {
  let validated = validate_card(req.card)?
  let charged   = charge_gateway(validated)?
  Ok(Receipt { id: UUID::new(), amount: charged })
}
```

---

## Aturan 2 — Zero-Copy untuk Data Besar (WAJIB untuk data lebih dari 1MB)

```omni
// SALAH — menyalin data besar
fn transfer(data: Vec<u8>) { ... }

// BENAR — kirim pointer
fn transfer(data: *const u8, len: usize) -> Result<(), IOError> {
  let slice = unsafe { rust::slice::from_raw_parts(data, len) }
  write_to_kernel_buffer(slice.toPointer())
}
```

---

## Aturan 3 — Domain Layer Segregation (WAJIB)

Setiap layer hanya boleh berisi bahasa yang ditentukan:

```
src/ui/       → TypeScript, HTML, Swift  (HANYA rendering)
src/domain/   → C#, Ruby, GraphQL        (HANYA business logic)
src/compute/  → Python, Julia, R         (HANYA komputasi)
src/system/   → C, C++, Rust             (HANYA low-level)
src/network/  → Go, JavaScript           (HANYA I/O & networking)
```

Komunikasi antar layer WAJIB melalui **OMNI Interface Bridge**:
```omni
// BENAR — via bridge
import { SalesData } from "@omni-bridge/domain/sales"

// SALAH — import langsung lintas layer
import { malloc } from "@omni-bridge/system/memory"  // UI tidak boleh sentuh memori
```

---

## Aturan 4 — Immutability First

```omni
// Default: immutable
immutable val config: AppConfig = load_config("app.toml")

// Jika memang perlu mutable, deklarasikan eksplisit
mutable var counter: AtomicU64 = AtomicU64::new(0)
```

---

## Aturan 5 — Permissions Minimal di Omnifile.toml

```toml
[permissions]
# BENAR — whitelist eksplisit
allow_net = ["api.stripe.com", "api.openai.com"]
allow_fs  = ["/tmp/mypackage/"]

# SALAH — jangan pernah wildcard
allow_net = ["*"]
allow_fs  = ["/"]
```

---

## Aturan 6 — Selalu Sertakan Test

Setiap fungsi publik HARUS memiliki minimal satu unit test:

```omni
#[test]
fn test_process_payment_success() {
  let req = PaymentRequest::mock_valid()
  assert!(process_payment(req).is_ok())
}

#[test]
fn test_process_payment_invalid_card() {
  let req = PaymentRequest::mock_invalid_card()
  assert!(process_payment(req).is_err())
}
```

---

*ANTIGRAVITY Skills — core/SKILL_rules.md*
