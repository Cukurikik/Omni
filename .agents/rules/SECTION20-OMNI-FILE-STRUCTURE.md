# 📁🧬 SECTION 20 — OMNI PROJECT FILE STRUCTURE (ARSITEKTUR FILE OMNI)

**ANTIGRAVITY MOTHER** memahami dan menegakkan struktur file proyek OMNI yang ketat, modular, dan polylingual. Setiap file memiliki tempat dan peran yang pasti dalam arsitektur universal. Struktur ini dirancang agar 15+ bahasa pemrograman hidup berdampingan dalam satu pohon direktori tanpa konflik, mematuhi aturan segregasi domain, dan dapat dikompilasi menjadi satu kesatuan oleh **LLVM‑Omni**.

### 20.1 — Filosofi Struktur File OMNI

- **Satu Proyek, Satu Pohon**: Tidak ada sub‑repositori atau sub‑modul yang terisolasi. Semua domain bahasa berbagi akar yang sama.
- **Segregasi Ketat per Layer**: Setiap layer (system, network, compute, domain, ui) memiliki direktori sendiri yang tidak boleh saling mengimpor secara langsung.
- **Konvensi Penamaan Universal**: File menggunakan ekstensi `.omni` untuk kode sumber utama, sementara file khusus bahasa dapat berada di subdirektori dengan ekstensi aslinya jika diperlukan.
- **Konfigurasi Deklaratif Tunggal**: `Omnifile.toml` adalah pusat kendali seluruh proyek.
- **Generated & Cache Terpisah**: Direktori `build/`, `.omni/`, dan `dist/` tidak pernah dimasukkan ke version control.

### 20.2 — Struktur Direktori Standar

```
my-omni-project/
├── Omnifile.toml                ← WAJIB — Manifest utama proyek
├── omnifile.lock                ← Auto-generated — Dependency lock
├── .omni/                       ← Cache & meta (tidak di-commit)
│   ├── index/                   ← Indeks proyek untuk IDE
│   └── artifacts/               ← Hasil build sementara
├── src/                         ← Kode sumber utama
│   ├── main.omni                ← Entry point aplikasi
│   ├── lib.omni                 ← Entry point library (jika ada)
│   ├── system/                  ← Layer Sistem (C, C++, Rust, Zig)
│   │   ├── alloc.c
│   │   ├── kernel_interface.cpp
│   │   └── memory_safety.rs
│   ├── network/                 ← Layer Jaringan & Konkurensi (Go, JS, Elixir)
│   │   ├── server.go
│   │   ├── event_loop.js
│   │   └── actor_system.ex
│   ├── compute/                 ← Layer Komputasi & Data (Python, Julia, R, Mojo)
│   │   ├── ml_pipeline.py
│   │   ├── simd_ops.jl
│   │   ├── stats.r
│   │   └── inference.mojo
│   ├── domain/                  ← Layer Bisnis (C#, GraphQL, Ruby, PHP, Java)
│   │   ├── order_aggregate.cs
│   │   ├── schema.graphql
│   │   ├── routes.rb
│   │   └── legacy_bridge.php
│   ├── ui/                      ← Layer Antarmuka (TypeScript, HTML, Swift, Dart)
│   │   ├── dashboard.ts
│   │   ├── layout.html
│   │   ├── ios_ui.swift
│   │   └── mobile_widget.dart
│   └── bridge/                  ← OMNI Interface Bridge (definisi antarmuka antar layer)
│       ├── system_to_network.omni
│       ├── domain_to_ui.omni
│       └── compute_to_domain.omni
├── tests/                       ← Pengujian
│   ├── unit/                    ← Test per fungsi/modul
│   │   ├── system/
│   │   ├── network/
│   │   ├── compute/
│   │   ├── domain/
│   │   └── ui/
│   ├── integration/             ← Test integrasi lintas layer
│   ├── e2e/                     ← End‑to‑end test
│   └── fuzz/                    ← Fuzzing corpus & test
├── config/                      ← File konfigurasi lingkungan
│   ├── default.toml
│   ├── development.toml
│   ├── staging.toml
│   └── production.toml
├── db/                          ← Database
│   ├── migrations/              ← Migration files (urutan)
│   │   ├── 001_init.up.sql
│   │   └── 001_init.down.sql
│   ├── seeds/                   ← Data seed
│   │   └── dev_sample.sql
│   └── schema/                  ← Definisi skema
│       └── current.graphql
├── assets/                      ← Aset statis
│   ├── images/
│   ├── fonts/
│   └── icons/
├── docs/                        ← Dokumentasi
│   ├── api/                     ← Auto-generated API docs
│   └── guides/
├── scripts/                     ← Skrip bantu (CI, devops)
├── build/                       ← Output build sementara (tidak di-commit)
├── dist/                        ← Hasil akhir executable & package
└── README.md
```

### 20.3 — Penjelasan Setiap Komponen

#### `Omnifile.toml` (WAJIB)

File konfigurasi tunggal yang mendefinisikan proyek, dependensi, permissions, target build, deployment, dan metadata lainnya. Inilah jantung dari proyek OMNI.

```toml
[package]
name    = "my-omni-project"
version = "0.1.0"
edition = "omni-2025"

[dependencies]
omni-std = "^2.0"

[build]
entry_point = "src/main.omni"
targets     = ["x86_64-linux", "wasm32"]

[permissions]
allow_net = ["api.example.com"]
allow_fs  = ["./data/**"]
```

#### `src/main.omni` atau `src/lib.omni`

Entry point aplikasi atau library. File ini dapat berisi kode dalam berbagai bahasa menggunakan anotasi OMNI, tetapi biasanya berisi logika orkestrasi tingkat tinggi.

```omni
// src/main.omni
use system::alloc;
use network::server;
use domain::order_handler;
use ui::dashboard;

fn main() -> Result<(), AppError> {
    let server = server::start()?;
    ui::launch(server.port())?;
    Ok(())
}
```

#### Direktori Layer

Setiap layer adalah direktori dengan kode dalam bahasa yang sesuai. File di dalamnya **hanya boleh menggunakan bahasa yang diizinkan** untuk layer tersebut. Komunikasi antar layer dilakukan melalui **OMNI Interface Bridge** yang didefinisikan di `src/bridge/`.

#### Direktori `src/bridge/`

Berisi file `.omni` yang mendefinisikan kontrak antar layer. File bridge ini adalah satu‑satunya tempat di mana dependensi lintas‑layer diizinkan.

```omni
// src/bridge/domain_to_ui.omni
pub bridge OrderPresenter {
    fn format_order(order: domain::Order) -> ui::OrderViewModel;
}
```

#### `tests/`

Struktur paralel dengan `src/`, berisi test untuk setiap layer. File test boleh menggunakan mock dan simulasi, tetapi tidak boleh berada di direktori `src/`.

#### `config/`

File konfigurasi per lingkungan, di‑load berdasarkan environment variable `OMNI_ENV`.

#### `db/`

Migrasi database, seed, dan definisi skema.

### 20.4 — Ekstensi File yang Didukung dalam Proyek OMNI

| Ekstensi              | Digunakan di Layer            | Keterangan         |
| :-------------------- | :---------------------------- | :----------------- |
| `.omni`               | Semua (terutama bridge, main) | File polyglot OMNI |
| `.c`, `.h`            | system                        | C source & header  |
| `.cpp`, `.hpp`, `.cc` | system                        | C++ source         |
| `.rs`                 | system                        | Rust source        |
| `.go`                 | network                       | Go source          |
| `.js`, `.mjs`         | network                       | JavaScript         |
| `.py`                 | compute                       | Python             |
| `.jl`                 | compute                       | Julia              |
| `.r`                  | compute                       | R                  |
| `.mojo`               | compute                       | Mojo               |
| `.cs`                 | domain                        | C#                 |
| `.graphql`            | domain                        | GraphQL schema     |
| `.rb`                 | domain                        | Ruby               |
| `.php`                | domain                        | PHP                |
| `.java`, `.kt`        | domain                        | Java / Kotlin      |
| `.ts`, `.tsx`         | ui                            | TypeScript         |
| `.html`, `.css`       | ui                            | Markup & style     |
| `.swift`              | ui                            | Swift              |
| `.dart`               | ui                            | Dart               |
| `.toml`               | root, config                  | Konfigurasi        |
| `.sql`                | db                            | SQL migration/seed |

### 20.5 — Aturan Besi Struktur File

1. **Tidak ada file yang menyentuh layer lain tanpa bridge.** Import langsung dari `../system/` ke `../ui/` akan ditolak oleh kompilator.
2. **File produksi tidak boleh mengandung test atau mock.** Lihat SECTION 17.
3. **Setiap fungsi publik wajib memiliki unit test di `tests/unit/` dengan path yang sesuai.**
4. **Seluruh file sumber harus dalam UTF‑8 tanpa BOM.**
5. **Dependency lock (`omnifile.lock`) wajib di‑commit untuk reproducibility.**
6. **Generated code (dari `omni generate`) hanya boleh berada di `build/` atau direktori khusus yang terdaftar di `.gitignore`.**
7. **File database migration tidak boleh diubah setelah diterapkan ke environment production — tambahkan migration baru.**

### 20.6 — Perintah CLI untuk Inspeksi Struktur

```bash
omni project validate     # Memeriksa apakah struktur proyek sesuai standar
omni project tree         # Menampilkan pohon proyek dengan anotasi layer
omni project lint         # Memeriksa pelanggaran aturan file
omni project init         # Membuat struktur proyek baru dari template
omni project doctor       # Diagnostik dan saran perbaikan struktur
```

### 20.7 — Template Proyek

Untuk memulai proyek baru:

```bash
omni project init my-new-project
cd my-new-project
omni project tree
```

Akan menghasilkan struktur standar lengkap dengan `Omnifile.toml`, direktori kosong, dan file contoh.
