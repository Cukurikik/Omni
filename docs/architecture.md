# OMNI Framework — Architecture Deep Dive

> Dokumen ini menjelaskan arsitektur internal OMNI Framework secara mendalam. Untuk quick start, lihat [README.md](../README.md).

---

## 1. Overview Arsitektur

OMNI Framework dibangun di atas tiga pilar fundamental:

### Pilar 1: Universal Abstract Syntax Tree (UAST)
Semua 15 bahasa pemrograman di-parse menjadi representasi AST tunggal. Ini memungkinkan:
- Interoperabilitas native tanpa FFI overhead
- Cross-language optimization oleh LLVM
- Type checking lintas bahasa pada compile time

### Pilar 2: Domain Layer Segregation
Kode dipisahkan ke dalam 5 domain layer yang ketat:

```
┌──────────────────────────────────────────┐
│          Interface Layer (UI)            │
│    TypeScript · HTML · Swift             │
├──────────────────────────────────────────┤
│          Business Layer (Logic)          │
│    GraphQL · C# · Ruby · PHP             │
├──────────────────────────────────────────┤
│          Compute Layer (Data)            │
│    Python · Julia · R                    │
├──────────────────────────────────────────┤
│         Network Layer (Concurrency)      │
│    Go · JavaScript                       │
├──────────────────────────────────────────┤
│          System Layer (Hardware)         │
│    C · C++ · Rust                        │
└──────────────────────────────────────────┘
```

**Rules:**
- Layer atas HANYA boleh berkomunikasi dengan layer di bawahnya melalui OMNI Bridge
- Layer bawah TIDAK BOLEH memiliki dependensi ke layer atas
- Setiap layer memiliki bahasa yang diperbolehkan — tidak bisa dicampur

### Pilar 3: Monadic Error System
Semua error ditangani melalui algebraic types:

```omni
enum Result<T, E> {
    Ok(T),
    Err(E),
}

// Operator ? untuk propagasi error
fn chain_operations() -> Result<FinalOutput, SomeError> {
    let step1 = operation_a()?    // propagate jika error
    let step2 = operation_b(step1)?
    let step3 = operation_c(step2)?
    Ok(step3)
}
```

---

## 2. Komponen Utama

### 2.1 Go API Gateway (`api/`)

Gateway HTTP/3 yang menangani semua request masuk dan mendistribusikannya ke language runtime yang tepat.

```
Request → Router → Orchestrator → Language Bridge → Runtime → Response
```

**Komponen:**
- `main.go` — Entry point dan server initialization
- `core/orchestrator.go` — Distribusi task ke language runtime
- `core/nexus_registry.go` — Interface ke OMNI-NEXUS
- `core/quarantine.go` — Sandbox untuk kode untrusted
- `engine/kinetic_bridge.go` — Bridge ke C/Rust native code
- `routes/` — HTTP handler definitions

### 2.2 OMNI Runtime Core (`omni-runtime/core/`)

Rust-based runtime yang mengelola memory, scheduling, dan execusi kode OMNI.

**Features:**
- Ownership-based memory management
- Green thread scheduler
- UAST interpreter
- JIT compilation via LLVM

### 2.3 Standard Library (`omni-runtime/stdlib/`)

Koleksi 40+ module native yang menyediakan functionality dasar:

```
stdlib/
├── omni/          # Core OMNI modules (fs, http, crypto, etc.)
├── rust/          # Rust interop primitives
├── go/            # Go concurrency bridges
├── python/        # Python ML/data bridges
├── typescript/    # TypeScript type system
├── c_cpp/         # C/C++ system headers
├── julia/         # Julia SIMD compute
├── r/             # R statistics
├── csharp/        # C# business logic
├── ruby/          # Ruby DSL/routing
├── php/           # PHP web lifecycle
├── swift/         # Swift UI components
├── graphql/       # GraphQL schema
└── html/          # HTML WASM host
```

### 2.4 OMNI-NEXUS Registry (`omni-runtime/nexus-registry/`)

Server registry yang mengelola distribusi dan resolusi package OMNI.

**Workflow:**
```
omni get crypto → Resolve deps → Download → Verify hash → Install → omni_modules/
```

### 2.5 Build Toolchain (`omni-runtime/toolchain/`)

Rust-based build system yang mengelola kompilasi lintas bahasa:

```
.omni source → Lexer → Parser → UAST → IR Generator → LLVM IR → Target binary
```

---

## 3. Data Flow

### 3.1 Request Lifecycle

```
1. Client mengirim HTTP request ke Go API Gateway
2. Router mencocokan path dan memilih handler
3. Orchestrator menentukan bahasa target dari kode sumber
4. Kinetic Bridge memuat native library jika diperlukan
5. UAST Engine mengeksekusi kode dengan context yang tepat
6. Result dikembalikan melalui monadic chain
7. Response di-serialize dan dikirim ke client
```

### 3.2 Package Resolution

```
1. Developer menulis Omnifile.toml dengan dependencies
2. `omni get` membaca manifest dan builds dependency graph
3. Resolver mencarikan versi kompatibel dari OMNI-NEXUS
4. Package didownload dan diverifikasi integritas hash-nya
5. Lock file (omni.lock) dihasilkan untuk reproducibility
6. Dependencies ditempatkan di omni_modules/
```

### 3.3 Cross-Language Function Call

```
TypeScript UI → OMNI Bridge → Go Network Layer → Rust System Layer
     ↓                              ↓                    ↓
 Type check            goroutine dispatch        memory-safe execution
     ↓                              ↓                    ↓
  JSX render            HTTP response           zero-copy data return
```

---

## 4. Security Model

### 4.1 Permission System

Setiap package mendeklarasikan permission di `Omnifile.toml`:

```toml
[permissions]
allow_net    = ["specific.api.com"]    # NO wildcards
allow_fs     = ["/tmp/app/"]           # Restricted paths
allow_env    = ["API_KEY"]             # Explicit env vars
allow_thread = true                     # Concurrency opt-in
allow_ffi    = false                    # Native code disabled
```

### 4.2 Quarantine Sandbox

Kode dari sumber untrusted dieksekusi di dalam sandbox isolasi:
- Memory limit enforcement
- CPU time limit
- Network access restriction
- Filesystem sandboxing

### 4.3 Supply Chain Security

OMNI-NEXUS mengimplementasikan:
- Package signature verification (Ed25519)
- Dependency audit logging
- Automated vulnerability scanning
- Reproducible build verification

---

## 5. Performance Characteristics

| Metric | OMNI | Node.js | JVM | .NET |
|--------|------|---------|-----|------|
| Cold start | <10ms | ~200ms | ~2s | ~500ms |
| Memory (hello world) | 3MB | 30MB | 100MB | 50MB |
| Cross-lang call | 0ns (zero-copy) | N/A | ~1μs (JNI) | ~1μs (P/Invoke) |
| Binary size | 3-8MB (unikernel) | N/A | ~200MB (JRE) | ~100MB (.NET Runtime) |
| Concurrency model | Green threads + goroutines | Event loop | OS threads | Task/Thread pool |

---

*Untuk pertanyaan mengenai arsitektur, buka [Discussion](https://github.com/Cukurikik/Omni/discussions) di GitHub.*
