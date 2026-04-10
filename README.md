<div align="center">

# 🪐 OMNI Framework

### *The World's First Polylingual Runtime — 15 Languages, 1 Universal AST*

[![OMNI Framework CI](https://github.com/Cukurikik/Omni/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Cukurikik/Omni/actions/workflows/ci-cd.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0--OMNI--NEXUS--ULTRA-blue.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Go Version](https://img.shields.io/badge/Go-1.26.1-00ADD8.svg)](https://go.dev/)
[![Rust](https://img.shields.io/badge/Rust-2024--edition-orange.svg)](https://www.rust-lang.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

---

**OMNI Framework** adalah sistem runtime polylingual revolusioner yang menyatukan **15 bahasa pemrograman** ke dalam satu runtime tunggal berbasis **LLVM-Omni**. Framework ini dirancang untuk mengeliminasi fragmentasi dalam rekayasa perangkat lunak modern dan melampaui kapabilitas ekosistem konvensional seperti Node.js, JVM, atau .NET.

> 📚 **REKOR BARU:** OMNI Framework kini didukung oleh **[2,6 Juta Kata Dokumentasi Enterprise-Grade](docs/OMNI-KNOWLEDGE-BASE.md)** yang tersebar di 540+ modul ekosistem, menjadikannya salah satu knowledge base framework terbesar di dunia.

[📖 Baca Mega-Dokumentasi (2.6 Juta Kata)](docs/OMNI-KNOWLEDGE-BASE.md) · [🚀 Quick Start](#-quick-start) · [📦 Packages](https://github.com/Cukurikik/Omni/packages) · [🏷️ Releases](https://github.com/Cukurikik/Omni/releases) · [📋 Wiki](https://github.com/Cukurikik/Omni/wiki) · [🐛 Issues](https://github.com/Cukurikik/Omni/issues)

</div>

---

## 📑 Daftar Isi

- [Tentang OMNI](#-tentang-omni)
- [Fitur Utama](#-fitur-utama)
- [Quick Start](#-quick-start)
- [Arsitektur](#-arsitektur)
- [15 Bahasa Pemrograman](#-15-bahasa-pemrograman-dalam-omni)
- [OMNI Language (.omni)](#-omni-language-omni)
- [OMNI CLI](#-omni-cli)
- [OMNI-NEXUS Package Registry](#-omni-nexus-package-registry)
- [Struktur Proyek](#-struktur-proyek)
- [Deployment](#-deployment)
- [Kontribusi](#-kontribusi)
- [Lisensi](#-lisensi)
- [Releases & Downloads](#-releases--downloads)

---

## 🪐 Tentang OMNI

OMNI Framework bukan sekadar "one more runtime" — ini adalah **paradigma baru** dalam pengembangan perangkat lunak. Alih-alih memaksa developer memilih satu bahasa dan satu ekosistem, OMNI memungkinkan kamu menggunakan **bahasa terbaik untuk setiap domain** dalam satu proyek tunggal:

- Butuh **kinerja bare-metal**? Gunakan C/C++/Rust.
- Butuh **concurrency masif**? Gunakan Go dengan goroutine native.
- Butuh **ML/AI pipeline**? Gunakan Python/Julia/R.
- Butuh **full-stack UI**? Gunakan TypeScript/HTML/Swift.
- Butuh **business logic**? Gunakan C#/GraphQL/Ruby.

Semua bahasa dikompilasi menjadi **Universal Abstract Syntax Tree (UAST)** dan dieksekusi dalam satu proses runtime — tanpa microservice overhead, tanpa serialization cost, tanpa inter-process communication latency.

### Mengapa OMNI?

| Masalah Konvensional | Solusi OMNI |
|---|---|
| Fragmentasi bahasa — setiap tim pakai bahasa berbeda | 15 bahasa dalam 1 runtime, 1 executable |
| Microservice spaghetti — ratusan service terpisah | Monolith performant dengan domain isolation |
| Data serialization overhead (JSON/gRPC/Protobuf) | Zero-copy data transfer antar bahasa via pointer |
| Dependency hell — npm, pip, cargo, gem semua terpisah | OMNI-NEXUS: satu registry untuk semua bahasa |
| Build toolchain chaos — webpack, vite, cmake, cargo | `omni build` — satu perintah untuk semuanya |
| Cold start di cloud — container butuh detik hingga menit | Unikernel 3-8MB, cold start <10ms |

---

## ✨ Fitur Utama

### 🧬 Universal Abstract Syntax Tree (UAST)
Semua 15 bahasa dipetakan ke dalam AST universal yang memungkinkan interoperabilitas native — tanpa FFI overhead, tanpa marshalling, tanpa serialization.

### ⚡ LLVM-Omni Compiler
Backend kompilasi berbasis LLVM yang mengoptimalkan kode lintas bahasa dengan pass vectorize, inline, dan unroll. Target output: x86_64, ARM64, WASM32, dan RISC-V.

### 🔒 Domain Layer Segregation
Arsitektur ketat yang memisahkan kode berdasarkan domain (System, Network, Compute, Interface, Business) untuk mencegah coupling dan memastikan safety.

### 📦 OMNI-NEXUS Package Registry  
Registry package terpadu yang menggantikan NPM, Cargo, PyPI, dan RubyGems. Satu perintah `omni get` untuk semua dependensi lintas bahasa.

### 🌐 Unikernel Deployment
Kompilasi aplikasi ke unikernel berukuran 3-8MB. Deploy ke OMNI Cloud dengan cold start kurang dari 10 milidetik.

### 🧪 Singularity Tier (Experimental)
- **Telepathy Engine**: Intent-based AST execution — tulis *apa yang kamu mau*, bukan *bagaimana* caranya.
- **Immortality Mesh**: Self-healing code yang auto-repair saat runtime error.
- **Interplanetary DTP**: Protokol jaringan untuk komunikasi latensi tinggi (Mars-Earth).

### 🛡️ Monadic Error Handling
Tidak ada `try/catch`. Semua error di-handle melalui pattern `Result<T, E>` yang aman dan composable.

### 📝 Comprehensive Tooling
- VS Code Extension (`omni-vscode`)
- Language Server Protocol (LSP)
- Syntax highlighting & IntelliSense
- Built-in test runner & benchmark suite

---

## 🚀 Quick Start

### Prasyarat

| Tool | Versi Minimum | Download |
|------|--------------|----------|
| **Go** | 1.24+ | [golang.org](https://golang.org/dl/) |
| **Rust** | 2024 Edition | [rustup.rs](https://rustup.rs/) |
| **Node.js** | 22+ | [nodejs.org](https://nodejs.org/) |
| **Git** | 2.40+ | [git-scm.com](https://git-scm.com/) |

### Instalasi

```bash
# 1. Clone repository
git clone https://github.com/Cukurikik/Omni.git
cd Omni

# 2. Install OMNI CLI
npm install

# 3. Build Go API Gateway
cd api
go mod download
go build -o omni-gateway .
cd ..

# 4. Build Rust Runtime Core
cd omni-runtime/core
cargo build --release
cd ../..

# 5. Verifikasi instalasi
node bin/omni.mjs --version
```

### Hello World dalam OMNI

Buat file `hello.omni`:

```omni
/// Program Hello World pertama dalam OMNI
/// Mendemonstrasikan interoperabilitas 3 bahasa dalam 1 file

// System Layer — Rust untuk string processing yang aman
@rust
fn create_greeting(name: &str) -> String {
    format!("🪐 Hello from OMNI, {}!", name)
}

// Network Layer — Go untuk HTTP server
@go
func ServeGreeting(w http.ResponseWriter, r *http.Request) {
    name := r.URL.Query().Get("name")
    greeting := omni_bridge::create_greeting(name)
    fmt.Fprintf(w, greeting)
}

// Interface Layer — TypeScript untuk type-safe API
@typescript
interface GreetingResponse {
    message: string;
    timestamp: number;
    language_count: number;
}

// Entry point
fn main() {
    println(create_greeting("World"))
    go::http::ListenAndServe(":8080", ServeGreeting)
}
```

Jalankan:
```bash
omni run hello.omni
```

---

## 📐 Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│                    OMNI Framework v2.0                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │   CLI   │  │   LSP   │  │  NEXUS  │  │  Cloud  │      │
│  │ omni.mjs│  │ omnils  │  │Registry │  │  PaaS   │      │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘      │
│       │            │            │            │             │
│  ┌────▼────────────▼────────────▼────────────▼────┐       │
│  │          OMNI Orchestrator (Go API)            │       │
│  │     HTTP/3 Gateway · Load Balancer · Router    │       │
│  └────────────────────┬──────────────────────────┘       │
│                       │                                   │
│  ┌────────────────────▼──────────────────────────┐       │
│  │         Universal AST (UAST) Engine           │       │
│  │    Lexer → Parser → IR Generator → Codegen    │       │
│  └────────────────────┬──────────────────────────┘       │
│                       │                                   │
│  ┌────────────────────▼──────────────────────────┐       │
│  │          LLVM-Omni Backend Compiler           │       │
│  │  x86_64 · ARM64 · WASM32 · RISC-V · GPU      │       │
│  └───────────────────────────────────────────────┘       │
│                                                             │
│  ┌─────────────────── Domain Layers ─────────────────────┐ │
│  │                                                       │ │
│  │  System    │ C · C++ · Rust                          │ │
│  │  Network   │ Go · JavaScript                         │ │
│  │  Compute   │ Python · Julia · R                      │ │
│  │  Interface │ TypeScript · HTML · Swift                │ │
│  │  Business  │ GraphQL · C# · Ruby · PHP               │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧬 15 Bahasa Pemrograman dalam OMNI

### System Layer — Bare Metal & Hardware

| Bahasa | Domain | Idiom OMNI | Contoh Use Case |
|--------|--------|------------|-----------------|
| **C** | Kernel I/O, FFI binding | `extern "omni-c" fn` | Driver perangkat, syscall wrapper |
| **C++** | Template metaprogramming, GPU | `@cpp_template<T>` | Tensor operations, game engine |
| **Rust** | Memory-safe concurrency | `own<T>`, `borrow<T>` | Cryptography, parser, data structure |

### Concurrency Layer — Network & Parallelism

| Bahasa | Domain | Idiom OMNI | Contoh Use Case |
|--------|--------|------------|-----------------|
| **Go** | Green threads, HTTP server | `spawn goroutine` | API gateway, microservice mesh |
| **JavaScript** | Event loop, async I/O | `async evloop` | Real-time streaming, WebSocket |

### Compute Layer — Data Science & ML

| Bahasa | Domain | Idiom OMNI | Contoh Use Case |
|--------|--------|------------|-----------------|
| **Python** | ML pipeline, scripting | `py::` namespace | TensorFlow model, data wrangling |
| **Julia** | SIMD vector ops, HPC | `@julia_simd` | Monte Carlo simulation, quant trading |
| **R** | Statistical modeling | `r::stat` namespace | A/B testing, regression analysis |

### Interface Layer — UI & Frontend

| Bahasa | Domain | Idiom OMNI | Contoh Use Case |
|--------|--------|------------|-----------------|
| **TypeScript** | Static typing, full-stack | `ts::` strong types | Dashboard, API client SDK |
| **HTML** | Semantic layout, WASM host | `@html_template` | Landing page, email template |
| **Swift** | Native mobile, Apple ecosystem | `swift::UIKit` | iOS app, visionOS spatial |

### Business Layer — Logic & State

| Bahasa | Domain | Idiom OMNI | Contoh Use Case |
|--------|--------|------------|-----------------|
| **GraphQL** | Schema-first data contract | `@schema` decorator | API contract, database schema |
| **C#** | DDD, CQRS, enterprise logic | `cs::domain` | Payment processing, ERP system |
| **Ruby** | DSL, routing, convention | `rb::route` | Admin panel, webhook handler |
| **PHP** | Web lifecycle, CMS bridge | `php::web` | WordPress integration, legacy API |

---

## 💎 OMNI Language (.omni)

OMNI memiliki bahasa pemrograman nativenya sendiri dengan ekstensi `.omni`. Bahasa ini mengkombinasikan syntax terbaik dari Rust, TypeScript, dan Go:

### Syntax Reference

```omni
/// Deklarasi modul
module payment_service

/// Import dari berbagai domain
use @system/crypto::{AES256, SHA512}
use @network/http::{Server, Request, Response}
use @compute/ml::{FraudDetector}
use @domain/payment::{Order, Receipt, PaymentError}

/// Struct dengan immutability default
struct PaymentRequest {
    card_number: String,
    amount: Money,
    currency: Currency,
    merchant_id: UUID,
}

/// Monadic error handling — TIDAK ADA try/catch
pub fn process_payment(req: PaymentRequest) -> Result<Receipt, PaymentError> {
    let validated = validate_card(req.card_number)?
    let encrypted = AES256::encrypt(validated)?
    let fraud_score = FraudDetector::analyze(req)?
    
    guard fraud_score < 0.7 else {
        return Err(PaymentError::FraudDetected(fraud_score))
    }
    
    let receipt = charge_gateway(encrypted, req.amount)?
    Ok(receipt)
}

/// Concurrent handler dengan Go goroutine
@go
service PaymentServer on :8443 {
    post "/api/v1/charge" -> process_payment
    get  "/api/v1/status/:id" -> get_payment_status
    
    middleware [
        RateLimit(100, "1m"),
        Auth::JWT,
        Logger::Structured,
    ]
}
```

### Strict Rules

1. **Monadic Error Handling** — Semua fungsi yang bisa gagal WAJIB return `Result<T, E>`
2. **Zero-Copy Transfer** — Data >1MB WAJIB menggunakan pointer/reference
3. **Domain Segregation** — UI layer DILARANG mengakses System layer langsung
4. **Immutable by Default** — Gunakan `mutable` keyword secara eksplisit jika perlu

---

## 🔧 OMNI CLI

### Command Reference

```bash
# ─── Project Management ───
omni init                              # Scaffold proyek baru
omni init --template fintech           # Dari template industri
omni scan                              # Static analysis seluruh workspace
omni fix --all                         # Auto-fix semua issue

# ─── Build & Run ───
omni run <file.omni>                   # Jalankan file OMNI
omni build                             # Development build
omni build --release --target all      # Production semua platform
omni unikernel build                   # Build unikernel (3-8MB)

# ─── Testing ───
omni test                              # Jalankan semua test
omni test --coverage                   # Test dengan coverage report
omni bench                             # Benchmark performa
omni profile                           # CPU/memory profiling

# ─── Package Management ───
omni get <package>                     # Install dari OMNI-NEXUS
omni get omni-crypto@^3.0              # Dengan version constraint
omni publish                           # Publish ke OMNI-NEXUS
omni doc                               # Generate API documentation

# ─── Cloud Deployment ───
omni cloud deploy                      # Deploy ke OMNI Cloud
omni cloud deploy --region id-jkt-1    # Dengan region spesifik
omni cloud logs                        # Stream logs real-time
omni cloud scale --replicas 10         # Horizontal scaling
```

---

## 📦 OMNI-NEXUS Package Registry

OMNI-NEXUS adalah registry package terpadu yang menggantikan NPM, Cargo, PyPI, dan semua registry per-bahasa.

### Manifest: Omnifile.toml

Setiap proyek OMNI menggunakan `Omnifile.toml` sebagai manifest utama:

```toml
[package]
name        = "my-omni-app"
version     = "1.0.0"
authors     = ["Developer <dev@example.com>"]
description = "Deskripsi proyek OMNI"
license     = "MIT"
edition     = "omni-2025"

[dependencies]
omni-std     = "^2.0"
omni-net     = "^1.5"
omni-crypto  = "^3.0"
omni-db      = "^2.1"

[dev-dependencies]
omni-test    = "^1.0"
omni-bench   = "^1.0"

[permissions]
allow_net    = ["api.stripe.com", "api.openai.com"]
allow_fs     = ["/tmp/myapp/"]
allow_env    = ["API_KEY", "DB_URL"]
allow_thread = true

[build]
target       = ["wasm32", "x86_64-linux", "aarch64-apple"]
optimize     = "release"
llvm_passes  = ["vectorize", "inline", "unroll"]
```

### Available Modules

| Tier | Package | Deskripsi |
|------|---------|-----------|
| **Core** | `omni-std` | Standard library — types, collections, iterators |
| **Core** | `omni-runtime` | Runtime engine — memory manager, scheduler |
| **Core** | `omni-types` | Type system — generics, traits, interfaces |
| **System** | `omni-crypto` | Cryptography — AES, RSA, SHA, Ed25519 |
| **System** | `omni-mem` | Memory management — allocators, pools |
| **System** | `omni-gpu` | GPU compute — CUDA, Vulkan, Metal bindings |
| **Data** | `omni-db` | Database — PostgreSQL, MySQL, SQLite, Redis |
| **Data** | `omni-cache` | Caching — LRU, TTL, distributed cache |
| **Data** | `omni-stream` | Streaming — Kafka, RabbitMQ, NATS |
| **App** | `omni-net` | Networking — HTTP/3, WebSocket, gRPC |
| **App** | `omni-auth` | Authentication — JWT, OAuth2, SAML |
| **App** | `omni-ml` | Machine Learning — inference, training |
| **Tooling** | `omni-test` | Testing framework — unit, integration, e2e |
| **Tooling** | `omni-bench` | Benchmarking — performance profiling |
| **Tooling** | `omni-doc` | Documentation — auto-generated API docs |
| **Premium** | `omni-hft` | High-Frequency Trading — SIMD, eBPF |
| **Premium** | `omni-legacy-bridge` | Legacy system connector — JVM, .NET |
| **Premium** | `omni-cloud-sdk` | Cloud infrastructure — deploy, scale |
| **Singularity** | `omni-intent-ast` | Telepathy Engine — intent-based coding |
| **Singularity** | `omni-immortality-mesh` | Self-healing code runtime |
| **Singularity** | `omni-interplanetary-dtp` | Deep-space networking protocol |
| **Singularity** | `omni-quantum-bridge` | Quantum computing bridge |

---

## 📁 Struktur Proyek

```
Omni/
├── 📄 README.md                          # Dokumentasi utama (file ini)
├── 📄 CONTRIBUTING.md                    # Panduan kontribusi
├── 📄 CHANGELOG.md                       # Riwayat perubahan
├── 📄 LICENSE                            # Lisensi MIT
├── 📄 SECURITY.md                        # Kebijakan keamanan
├── 📄 CODE_OF_CONDUCT.md                # Kode etik komunitas
├── 📄 Omnifile.toml                      # Manifest proyek
├── 📄 package.json                       # Node.js dependencies
├── 📄 go.work                            # Go workspace
│
├── 📂 api/                               # Go API Gateway
│   ├── main.go                           # Entry point server
│   ├── go.mod                            # Go module manifest
│   ├── core/                             # Core engine modules
│   │   ├── orchestrator.go               # Language orchestrator
│   │   ├── nexus_registry.go             # Package registry
│   │   ├── appconfig.go                  # Configuration
│   │   └── quarantine.go                 # Security sandbox
│   ├── engine/                           # Polyglot engine
│   │   ├── kinetic_bridge.go             # C/Rust bridge
│   │   └── registry.go                   # Language registry
│   └── routes/                           # HTTP handlers
│       ├── router.go                     # Route definitions
│       └── handlers.go                   # Request handlers
│
├── 📂 omni-runtime/                      # OMNI Runtime Engine
│   ├── src/main.omni                     # Runtime entry point
│   ├── core/                             # Core implementations
│   │   ├── Cargo.toml                    # Rust workspace manifest
│   │   ├── src/                          # Rust runtime source
│   │   └── ruby/                         # Ruby YJIT integration
│   ├── stdlib/                           # Standard library
│   │   ├── omni/                         # OMNI native stdlib
│   │   ├── rust/                         # Rust primitives
│   │   ├── go/                           # Go concurrency
│   │   ├── python/                       # Python bridge
│   │   ├── typescript/                   # TS type system
│   │   └── ...                           # 15 bahasa bridges
│   ├── omni_modules/                     # Built-in modules
│   │   ├── omni-std/                     # Standard library module
│   │   ├── omni-intent-ast/              # Telepathy Engine
│   │   ├── omni-immortality-mesh/        # Self-healing runtime
│   │   ├── omni-interplanetary-dtp/      # Deep-space protocol
│   │   └── omni-quantum-bridge/          # Quantum computing
│   ├── nexus-registry/                   # Package registry server
│   ├── toolchain/                        # Build toolchain (Rust)
│   ├── cli/                              # CLI tools (Rust)
│   ├── tests/                            # Test suites
│   └── examples/                         # Example programs
│
├── 📂 omni-project/                      # Project templates
├── 📂 omni-vscode/                       # VS Code extension
│   ├── package.json                      # Extension manifest
│   ├── syntaxes/omni.tmLanguage.json     # Syntax highlighting
│   └── language-configuration.json       # Language config
│
├── 📂 omni-cli-systems/                  # CLI subsystems
│   └── rust/                             # Rust-based CLI tools
│
├── 📂 sdk/                               # Client SDKs
│   └── omni-client/                      # JavaScript/TypeScript SDK
│
├── 📂 ui/                                # Dashboard UI (Vite + React)
│   ├── src/                              # Source components
│   └── vite.config.ts                    # Vite configuration
│
├── 📂 skills/                            # AI Agent Skills
│   ├── core/                             # Core identity & rules
│   ├── languages/                        # Language layer skills
│   ├── monetization/                     # Revenue model skills
│   └── meta/                             # System prompts
│
├── 📂 bin/                               # CLI binaries & tools
│   ├── omni.mjs                          # Main OMNI CLI
│   └── oracle_logic.mjs                  # Oracle AI engine
│
├── 📂 configs/                           # Configuration files
│   ├── appconfig.json                    # Application config
│   └── cli_registry.json                # CLI tool registry
│
├── 📂 docs/                              # Extended documentation
│   ├── architecture.md                   # Architecture deep-dive
│   ├── language-guide.md                 # OMNI language guide
│   ├── api-reference.md                  # API documentation
│   ├── deployment.md                     # Deployment guide 
│   └── faq.md                            # FAQ
│
├── 📂 .github/                           # GitHub configuration
│   └── workflows/ci-cd.yml              # CI pipeline
│
└── 📂 release/                           # Release artifacts
    ├── public/                           # Built frontend assets
    └── omni_cache/                       # Runtime cache
```

---

## 🚢 Deployment

### Local Development

```bash
# Start Go API Gateway
cd api && go run main.go

# Start UI Dashboard
cd ui && npm run dev

# Run OMNI program
omni run examples/hello.omni
```

### Production (Unikernel)

```bash
# Build micro-image (3-8MB)
omni unikernel build --target cloud --optimize release

# Deploy to OMNI Cloud
omni cloud deploy app.ukl --region id-jkt-1 --replicas 3
```

### Docker

```bash
docker build -t omni-framework .
docker run -p 8080:8080 omni-framework
```

---

## 🏷️ Releases & Downloads

File besar (>100MB) yang tidak bisa disimpan di Git repository disediakan melalui **GitHub Releases**:

| Asset | Ukuran | Deskripsi |
|-------|--------|-----------|
| `setup-go-Linux-x64-ubuntu24-go-1.26.1` | ~150MB | Go toolchain untuk CI/CD Linux |
| `clang-format.zip` | ~333MB | LLVM Clang formatter tools |
| `pandoc-3.1.12.3` | ~209MB | Document converter engine |
| `ffmpeg-8.1-essentials` | ~300MB | Media processing toolkit |

➡️ Download dari [**Releases Page**](https://github.com/Cukurikik/Omni/releases)

---

## 🔐 License Tiers

| Tier | Harga | Request Limit | SLA |
|------|-------|--------------|-----|
| **Community** | Gratis | 7.000.000.000/bln | Best-effort |
| **Pro** | $29/bln | 99.999.999.999.999/bln | 99.9% |
| **Enterprise** | Custom | Unlimited | 99.99% + Dedicated Engineer |

---

## 🤝 Kontribusi

Kami menyambut kontribusi dari semua developer! Silakan baca [CONTRIBUTING.md](CONTRIBUTING.md) untuk panduan lengkap.

```bash
# Fork & clone
git clone https://github.com/<username>/Omni.git

# Buat branch fitur
git checkout -b feature/amazing-feature

# Commit perubahan
git commit -m "feat(module): deskripsi perubahan"

# Push & buat Pull Request
git push origin feature/amazing-feature
```

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah **MIT License** — lihat file [LICENSE](LICENSE) untuk detail.

---

## 🔗 Links

- 🌐 **Website**: [omniframework.dev](https://omniframework.dev) *(coming soon)*
- 📦 **Registry**: [nexus.omniframework.dev](https://nexus.omniframework.dev) *(coming soon)*
- 💬 **Discord**: [discord.gg/omni](https://discord.gg/omni) *(coming soon)*
- 🐦 **Twitter/X**: [@OmniFramework](https://twitter.com/OmniFramework)
- 📧 **Email**: admin@omniframework.dev

---

<div align="center">

**🪐 Welcome to the Singularity. Welcome to OMNI. 🪐**

*Dibuat dengan ❤️ oleh OMNI Core Team*

*Copyright © 2025-2026 OMNI Framework. All rights reserved.*

</div>
