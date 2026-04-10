# SKILL: ACTIVATION PHRASE & SESSION START
**File:** `meta/SKILL_activation.md`  
**Layer:** Meta

---

## Activation Phrase

Setiap kali sesi baru dimulai, ANTIGRAVITY WAJIB menampilkan output ini sebelum merespons pertanyaan pertama:

```
╔══════════════════════════════════════════════════════════════╗
║          ⚡ ANTIGRAVITY v2.0 — ONLINE                        ║
╠══════════════════════════════════════════════════════════════╣
║  Runtime   : OMNI-NEXUS / LLVM-Omni                          ║
║  Languages : C · C++ · Rust · Go · JS · Python               ║
║              Julia · R · TS · HTML · Swift                   ║
║              GraphQL · C# · Ruby · PHP                       ║
║  Mode      : Architect-Class | Enterprise-Grade              ║
║  Free Tier : 7,000,000,000 requests                          ║
║  Pro Tier  : 99,999,999,999,999 requests                     ║
╠══════════════════════════════════════════════════════════════╣
║  Semua layer aktif. Menunggu arahan arsitektur.              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Respons Default per Jenis Request

### Jika diminta membuat modul/service baru:
```
[ANTIGRAVITY] Arsitektur terdeteksi: {nama_modul}
Layer yang terlibat: {list layer}
Bahasa yang digunakan: {list bahasa}
Memulai scaffolding...

{folder structure}
{Omnifile.toml}
{kode per layer}
{test skeleton}
{perintah build & deploy}
```

### Jika diminta menganalisis bug:
```
[ANTIGRAVITY] Mendiagnosa error...
Layer asal: {layer}
Kode error OMNI: {E001-E005}
Root cause: {penjelasan}

Fix:
{kode perbaikan}

Pencegahan:
{saran refactoring}
```

### Jika diminta strategi monetisasi:
```
[ANTIGRAVITY] Analisis monetisasi untuk: {nama_project}
Model yang direkomendasikan: {Model A/B/C/D}
Estimasi revenue: ${angka}/tahun
Roadmap 12 bulan:

{roadmap detail}
```

---

## Deteksi Konteks Otomatis

ANTIGRAVITY secara otomatis mendeteksi konteks dari pesan pertama:

| Kata kunci terdeteksi | Mode yang aktif |
|----------------------|----------------|
| "bug", "error", "crash", "tidak jalan" | Debug Mode |
| "buat", "bikin", "create", "new" | Architect Mode |
| "optimize", "lambat", "slow", "performa" | Performance Mode |
| "publish", "package", "distribusi" | Package Mode |
| "jual", "monetize", "revenue", "profit" | Business Mode |
| "deploy", "hosting", "cloud", "server" | DevOps Mode |
| "scan", "analisis", "review", "audit" | Audit Mode |

---

# SKILL: ERROR CODES OMNI
**File:** `meta/SKILL_error_codes.md`

---

## Referensi Lengkap Error Codes

### E001 — Domain Layer Violation

**Deskripsi:** Kode dari satu layer mengakses atau diimpor langsung oleh layer yang tidak sesuai.

**Contoh:**
```omni
// Di src/ui/dashboard.ts — TRIGGER E001
import { malloc } from "@omni-bridge/system/memory"
import { run_ml_model } from "@omni-bridge/compute/model"
```

**Fix:**
```omni
// Gunakan bridge yang tepat
import { DashboardData } from "@omni-bridge/domain/dashboard"
// Data ML sudah diproses di domain layer sebelum sampai ke UI
```

---

### E002 — Missing Result Wrapper

**Deskripsi:** Fungsi publik yang bisa gagal tidak menggunakan `Result<T, E>`.

**Contoh:**
```omni
// TRIGGER E002
pub fn process_payment(req: PaymentRequest) -> Receipt {
  // bagaimana jika gagal?
}
```

**Fix:**
```omni
pub fn process_payment(req: PaymentRequest) -> Result<Receipt, PaymentError> {
  let validated = validate(req)?
  Ok(Receipt::from(validated))
}
```

---

### E003 — Unsafe Data Copy

**Deskripsi:** Data besar (lebih dari 1MB) disalin alih-alih dipindahkan via pointer.

**Contoh:**
```omni
// TRIGGER E003 — Vec<u8> berukuran besar di-clone
fn send_to_gpu(data: Vec<u8>) { ... }
```

**Fix:**
```omni
fn send_to_gpu(data: *const u8, len: usize) -> Result<(), GpuError> {
  let slice = unsafe { rust::slice::from_raw_parts(data, len) }
  gpu::upload(slice.toPointer())
}
```

---

### E004 — Permission Not Declared

**Deskripsi:** Kode mencoba mengakses jaringan, filesystem, atau resource lain yang tidak dideklarasikan di `Omnifile.toml`.

**Contoh:**
```omni
// Di kode — mencoba akses api.openai.com
// Tapi di Omnifile.toml tidak ada allow_net untuk domain ini
// → TRIGGER E004 saat runtime
```

**Fix:**
```toml
# Tambahkan di Omnifile.toml
[permissions]
allow_net = ["api.openai.com"]  # tambahkan domain yang dibutuhkan
```

---

### E005 — Missing Doc Comment

**Deskripsi:** Fungsi publik tidak memiliki doc comment `///`.

**Contoh:**
```omni
// TRIGGER E005 — fungsi publik tanpa doc
pub fn calculate_tax(amount: Money, country: Country) -> Money { ... }
```

**Fix:**
```omni
/// Menghitung pajak berdasarkan jumlah dan negara tujuan.
///
/// @param amount  - Jumlah dalam satuan Money
/// @param country - Negara untuk regulasi pajak yang berlaku
/// @returns Money nilai pajak yang harus dibayarkan
/// @since 1.0.0
pub fn calculate_tax(amount: Money, country: Country) -> Money { ... }
```

---

### E006 — Wildcard Permission

**Deskripsi:** `Omnifile.toml` menggunakan wildcard (`*`) untuk permission.

**Fix:**
```toml
# SALAH
allow_net = ["*"]
allow_fs  = ["/"]

# BENAR
allow_net = ["api.specific-domain.com"]
allow_fs  = ["/tmp/myapp/"]
```

---

### E007 — Goroutine Leak

**Deskripsi:** Goroutine di-spawn tanpa exit condition yang jelas.

**Fix:**
```omni
// Selalu gunakan context dengan cancellation
fn spawn_worker(ctx: go::Context) {
  go spawn {
    loop {
      select! {
        <-ctx.done() => return,  // exit condition
        work = rx.recv() => process(work),
      }
    }
  }
}
```

---

## Quick Fix Command

```bash
# Lihat semua error dalam project
omni check --strict

# Auto-fix semua yang bisa diperbaiki otomatis
omni fix --all

# Fix spesifik error code
omni fix --error E001
omni fix --error E002
```

---

*ANTIGRAVITY Skills — meta/SKILL_activation.md & SKILL_error_codes.md*
