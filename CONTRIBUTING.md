# Contributing to OMNI Framework

Terima kasih telah tertarik untuk berkontribusi pada OMNI Framework! 🪐

Dokumen ini memberikan panduan dan instruksi agar kontribusi Anda berjalan lancar.

---

## 📋 Daftar Isi

- [Code of Conduct](#code-of-conduct)
- [Cara Berkontribusi](#cara-berkontribusi)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Convention](#commit-convention)
- [Pull Request Process](#pull-request-process)
- [Domain Layer Rules](#domain-layer-rules)
- [Testing](#testing)
- [Dokumentasi](#dokumentasi)

---

## Code of Conduct

Proyek ini mengikuti [Code of Conduct](CODE_OF_CONDUCT.md) kami. Dengan berpartisipasi, Anda diharapkan mematuhi kode ini.

---

## Cara Berkontribusi

### 🐛 Melaporkan Bug
1. Periksa [Issues](https://github.com/Cukurikik/Omni/issues) apakah bug sudah dilaporkan
2. Buat issue baru dengan template bug report
3. Sertakan langkah reproduksi, expected behavior, dan actual behavior

### 💡 Mengajukan Fitur
1. Buka [Discussions](https://github.com/Cukurikik/Omni/discussions) untuk diskusi awal
2. Jika disetujui, buat issue dengan label `enhancement`
3. Tunggu approval dari core maintainer sebelum mulai koding

### 🔧 Mengirim Kode
1. Fork repository
2. Buat branch dari `main` dengan nama deskriptif
3. Tulis kode sesuai coding standards
4. Tambahkan test yang relevan
5. Submit Pull Request

---

## Development Setup

### Prasyarat

```bash
# Go 1.24+
go version

# Rust (latest stable)
rustup show

# Node.js 22+
node --version

# Git 2.40+
git --version
```

### Setup Langkah demi Langkah

```bash
# 1. Fork dan clone
git clone https://github.com/<your-username>/Omni.git
cd Omni

# 2. Install Node.js dependencies
npm install

# 3. Setup Go modules
cd api && go mod download && cd ..

# 4. Setup Rust toolchain
cd omni-runtime/core && cargo build && cd ../..

# 5. Verifikasi
node bin/omni.mjs --version
```

---

## Coding Standards

### OMNI Strict Rules (WAJIB)

#### 1. Monadic Error Handling
```omni
// ❌ DILARANG
try {
    processPayment()
} catch (e) {
    console.error(e)
}

// ✅ WAJIB
fn process_payment(req: Request) -> Result<Receipt, PaymentError> {
    let validated = validate(req)?
    let charged = charge(validated)?
    Ok(Receipt::new(charged))
}
```

#### 2. Domain Layer Segregation
```
src/
├── ui/           → HANYA TypeScript, HTML, Swift
├── domain/       → HANYA C#, Ruby, GraphQL
├── compute/      → HANYA Python, Julia, R
├── system/       → HANYA C, C++, Rust
└── network/      → HANYA Go, JavaScript
```

#### 3. Immutable by Default
```omni
// Default: immutable
val config: AppConfig = load_config()

// Eksplisit jika perlu mutable
mutable var counter: AtomicU64 = AtomicU64::new(0)
```

#### 4. Zero-Copy untuk Data >1MB
```omni
// ❌ SALAH — copy data besar
fn transfer(data: Vec<u8>) { ... }

// ✅ BENAR — gunakan reference
fn transfer(data: &[u8]) -> Result<(), IOError> { ... }
```

### Go Standards
- Gunakan `gofmt` untuk formatting
- Semua error harus di-handle (no `_` untuk error)
- Gunakan `context.Context` untuk cancellation

### Rust Standards
- Gunakan `rustfmt` dan `clippy`
- Prefer `&str` over `String` untuk function parameters
- Dokumentasikan semua public items

### TypeScript Standards
- Strict mode aktif (`"strict": true`)
- Prefer `interface` over `type` untuk object shapes
- No `any` — gunakan `unknown` jika tipe belum diketahui

---

## Commit Convention

Kami menggunakan [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Deskripsi |
|------|-----------|
| `feat` | Fitur baru |
| `fix` | Bug fix |
| `docs` | Perubahan dokumentasi |
| `style` | Formatting, titik koma, dll (bukan perubahan logika) |
| `refactor` | Refactoring tanpa perubahan fungsional |
| `perf` | Peningkatan performa |
| `test` | Menambah/memperbaiki test |
| `chore` | Maintenance tasks |

### Scopes

| Scope | Area |
|-------|------|
| `core` | omni-runtime/core |
| `api` | Go API Gateway |
| `cli` | OMNI CLI tools |
| `nexus` | Package registry |
| `ui` | Dashboard UI |
| `docs` | Documentation |
| `ci` | CI/CD pipeline |

### Contoh

```
feat(core): implement UAST parser for Python bridge
fix(api): resolve goroutine leak in websocket handler
docs(readme): add Quick Start section
perf(nexus): optimize dependency resolution algorithm
test(core): add unit tests for lexer module
```

---

## Pull Request Process

1. **Update dokumentasi** jika perubahan Anda mempengaruhi public API
2. **Pastikan CI hijau** — semua check harus pass
3. **Minta review** dari minimal 1 core maintainer
4. **Squash commits** sebelum merge jika ada banyak commit kecil
5. **Gunakan merge commit** (bukan rebase) untuk PR merge

### PR Title Format
Sama dengan commit convention:
```
feat(core): deskripsi singkat perubahan
```

### PR Template
```markdown
## Deskripsi
Jelaskan perubahan yang dilakukan.

## Jenis Perubahan
- [ ] Fitur baru (non-breaking)
- [ ] Bug fix (non-breaking)
- [ ] Breaking change

## Testing
- [ ] Unit test ditambahkan/diperbarui
- [ ] Test lokal berhasil
- [ ] CI pipeline hijau

## Checklist
- [ ] Kode mengikuti coding standards
- [ ] Dokumentasi diperbarui
- [ ] Tidak ada console.log/println debugging
```

---

## Testing

```bash
# Go tests
cd api && go test ./... -v

# Rust tests
cd omni-runtime/core && cargo test

# OMNI tests (jika tersedia)
omni test --all --coverage
```

### Testing Requirements
- Semua fungsi publik **WAJIB** memiliki minimal 1 unit test
- Coverage target: **80%** untuk core modules
- Integration test untuk setiap API endpoint

---

## Dokumentasi

- Semua fungsi publik harus memiliki doc comment
- Update README.md jika menambah fitur baru
- Update CHANGELOG.md untuk setiap perubahan signifikan

```omni
/// Memproses transaksi pembayaran.
///
/// @param req - Data pembayaran yang akan diproses
/// @returns Result<Receipt, PaymentError>
/// @example
///   let result = process_payment(req)?
/// @since 2.0.0
pub fn process_payment(req: PaymentRequest) -> Result<Receipt, PaymentError> {
    // ...
}
```

---

## 🙏 Terima Kasih

Setiap kontribusi, sekecil apapun, sangat berarti bagi perkembangan OMNI Framework. Kami menghargai waktu dan usaha Anda!

> *"The singularity is not a destination — it's a collaboration."* — OMNI Core Team
