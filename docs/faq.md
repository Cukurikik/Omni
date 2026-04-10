# Frequently Asked Questions (FAQ)

---

## Umum

### Apa itu OMNI Framework?
OMNI Framework adalah runtime polylingual yang menyatukan 15 bahasa pemrograman ke dalam satu executable tunggal berbasis LLVM. Alih-alih menggunakan microservices terpisah untuk setiap bahasa, OMNI memungkinkan semua bahasa berjalan dalam satu proses dengan zero-copy data transfer.

### Mengapa membutuhkan 15 bahasa?
Setiap bahasa memiliki kekuatan domain-nya masing-masing. C/Rust untuk performa, Go untuk concurrency, Python untuk ML, TypeScript untuk UI. OMNI memungkinkan developer menggunakan alat terbaik untuk setiap domain tanpa overhead integrasi.

### Apakah OMNI menggantikan Node.js?
OMNI dirancang untuk melampaui kemampuan Node.js dengan menawarkan native concurrency (bukan hanya event loop), memory safety (bukan garbage collection saja), dan interoperabilitas multi-bahasa. Untuk single-language JavaScript projects, Node.js mungkin masih sesuai.

### Apakah OMNI production-ready?
OMNI v2.0 adalah **Architecture Release** — semua komponen fondasi sudah ada, termasuk runtime core, API gateway, package manager, dan CLI. Singularity Tier (Telepathy, Immortality Mesh) masih eksperimental.

---

## Teknis

### Bagaimana interoperabilitas antar bahasa bekerja?
Semua bahasa dikompilasi menjadi Universal Abstract Syntax Tree (UAST). Fungsi dari bahasa apapun dapat dipanggil dari bahasa lain melalui OMNI Bridge Protocol tanpa serialization atau FFI overhead — data di-share melalui pointer (zero-copy).

### Bagaimana dengan memory management?
OMNI menggunakan model ownership terinspirasi Rust. Variabel memiliki pemilik tunggal, dan lifetime ditentukan pada compile time. Untuk area yang membutuhkan manual management (C/C++), kode harus berada di dalam `unsafe_zone` block.

### Bahasa pemrograman apa yang diperlukan untuk berkontribusi?
Minimal: **Go** (untuk API Gateway) dan **Rust** (untuk Runtime Core). Untuk frontend: **TypeScript**. Untuk memahami full stack, pengetahuan dasar tentang semua 15 bahasa sangat membantu.

### Apakah OMNI mendukung Windows?
Ya! OMNI mendukung Windows, Linux, dan macOS. Go API Gateway dikompilasi tanpa CGO dependency (pure Go) untuk kompatibilitas maksimal di Windows.

---

## Package & Deployment

### Bagaimana cara menginstall package OMNI?
Gunakan `omni get <package-name>`. Package diinstall ke folder `omni_modules/` dan dependency tree tercatat di `omni.lock`.

### Berapa ukuran binary OMNI?
Unikernel deployment: **3-8MB**. Standard binary: **30-50MB**. Jauh lebih kecil dari JVM (~200MB) atau .NET Runtime (~100MB).

### Bagaimana deployment ke production?
Tiga opsi: (1) **Unikernel** ke OMNI Cloud, (2) **Docker container**, atau (3) **Binary langsung** ke VPS. Lihat [Deployment Guide](docs/deployment.md).

---

## Lisensi & Pricing

### Apakah OMNI gratis?
Ya, OMNI Framework core (runtime, CLI, standard library) dilisensikan MIT — 100% gratis dan open source. Premium packages di OMNI-NEXUS registry mungkin memiliki harga terpisah.

### Apa perbedaan tier Community, Pro, dan Enterprise?
- **Community**: Gratis, 7 miliar request/bulan, best-effort support
- **Pro**: $29/bulan, 99.9 triliun request/bulan, SLA 99.9%
- **Enterprise**: Custom pricing, unlimited, dedicated engineer, SLA 99.99%

---

*Pertanyaan lain? Buka [Discussion](https://github.com/Cukurikik/Omni/discussions)*
