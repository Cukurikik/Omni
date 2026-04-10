# SKILL: WORKSPACE SCAN & ANALYSIS
**File:** `ide/SKILL_workspace_scan.md`  
**Layer:** IDE Integration

---

## Cara Kerja Workspace Scan

Saat `omni scan` dijalankan, ANTIGRAVITY membaca seluruh workspace dan membangun model pemahaman lengkap:

```
omni scan
→ [1/6] Membaca struktur direktori...
→ [2/6] Parsing 15 bahasa ke UAST (Universal AST)...
→ [3/6] Membangun dependency graph...
→ [4/6] Mendeteksi layer violations (E001)...
→ [5/6] Menjalankan security audit...
→ [6/6] Menganalisis performa hotspot...

Scan selesai. Ditemukan:
  - 3 layer violations (E001)
  - 7 fungsi tanpa error handling (E002)
  - 2 permission tidak terdeklarsai (E004)
  - 12 fungsi tanpa doc comment (E005)
  - 1 goroutine potential leak (E007)
  - 4 fungsi dengan kompleksitas tinggi (CC > 10)
  - 2 dependency dengan CVE aktif

Jalankan `omni fix --all` untuk memperbaiki otomatis.
Jalankan `omni audit --detail` untuk laporan keamanan lengkap.
```

---

## Output Laporan Scan

### Layer Violation Report
```
E001 LAYER VIOLATION — 3 ditemukan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] src/ui/dashboard.ts:42
    import { fraud_score } from "@omni-bridge/compute/fraud"
    → UI layer tidak boleh import langsung dari compute layer
    → Fix: Tambahkan domain/dashboard.cs sebagai mediator

[2] src/domain/payment.cs:18
    import { malloc } from "@omni-bridge/system/memory"
    → Domain layer tidak boleh akses system layer langsung
    → Fix: Bungkus dengan Rust wrapper di system layer dulu

[3] src/network/gateway.go:91
    import { GradientBoost } from "@omni-bridge/compute/models"
    → Network layer tidak boleh import ML models langsung
    → Fix: Jadikan domain layer sebagai orchestrator
```

### Dependency Graph Visualization
```
omni scan --graph
→ Output: ./target/dependency_graph.svg

Contoh output (text):
payment-gateway
├── [system] crypto.rs
│   └── omni-crypto@3.1.2
├── [network] gateway.go
│   ├── omni-net@1.5.0
│   └── [domain] payment.cs ← bridge
│       ├── omni-db@2.1.0
│       └── [compute] fraud.py ← bridge
│           └── omni-ml@1.0.3
└── [ui] dashboard.tsx
    └── [domain] payment.cs ← bridge (shared)
```

---

## Analisis Performa

```bash
omni profile --hotspot
→ Top 5 fungsi terlambat:
  1. compute::fraud_detect::predict()      → 45ms avg  ← LAMBAT
  2. system::crypto::encrypt_card_data()  → 12ms avg
  3. network::gateway::route_request()    → 8ms avg
  4. domain::payment::validate_card()     → 3ms avg
  5. domain::payment::charge_gateway()    → 2ms avg

Rekomendasi:
  - compute::fraud_detect::predict(): Tambahkan @julia_simd, estimasi 2ms
  - system::crypto::encrypt_card_data(): Gunakan hardware AES, estimasi 1ms
```

---

## Security Audit Detail

```bash
omni audit --detail
→ Laporan Keamanan OMNI
  ━━━━━━━━━━━━━━━━━━━━━━

  KRITIKAL (0):
  Tidak ada.

  TINGGI (1):
  [H001] src/system/crypto.rs:67
         Nonce generator menggunakan pseudo-random — ganti dengan CSPRNG
         Fix: Ganti rand::random() dengan rand::rngs::OsRng

  SEDANG (2):
  [M001] Omnifile.toml — allow_env = ["*"] terlalu luas
         Fix: Daftarkan env vars yang dibutuhkan secara eksplisit
  [M002] omni-db@2.1.0 — CVE-2024-1234 (SQL injection via raw query)
         Fix: omni update omni-db

  INFO (3):
  [I001] Tidak ada rate limiting pada endpoint POST /payments
  [I002] Log berisi data kartu (masked) — pertimbangkan enkripsi log
  [I003] Tidak ada audit trail untuk operasi admin
```

---

*ANTIGRAVITY Skills — ide/SKILL_workspace_scan.md*
