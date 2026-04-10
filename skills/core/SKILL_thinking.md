# SKILL: POLA PIKIR & DECISION TREE
**File:** `core/SKILL_thinking.md`  
**Layer:** Core  
**Token Count:** ~500

---

## Decision Tree 1 — Saat Menerima Request Kode

```
LANGKAH 1: SCAN
  → Identifikasi domain layer mana yang terlibat
  → Apakah ini system, compute, network, domain, atau ui?

LANGKAH 2: MAP
  → Tentukan bahasa yang paling tepat per domain
  → Lihat SKILL_layer_*.md untuk referensi

LANGKAH 3: ARCH
  → Rancang interface bridge antar layer jika perlu
  → Buat struktur folder terlebih dahulu

LANGKAH 4: CODE
  → Tulis kode dengan semua aturan dari SKILL_rules.md
  → Pastikan setiap fungsi publik ada return Result<T,E>

LANGKAH 5: TEST
  → Sertakan unit test minimal 2 kasus per fungsi publik

LANGKAH 6: DOC
  → Tambahkan doc comments standar (lihat SKILL_documentation.md)

LANGKAH 7: SHIP
  → Berikan struktur folder lengkap dan perintah deployment
```

---

## Decision Tree 2 — Saat Menganalisis Bug

```
LANGKAH 1: Baca stack trace → identifikasi layer asal error
LANGKAH 2: Cek pelanggaran Domain Segregation (E001)
LANGKAH 3: Cek penggunaan try/catch non-monadic (E002)
LANGKAH 4: Cek data copy yang seharusnya zero-copy (E003)
LANGKAH 5: Cek permission yang hilang di Omnifile.toml (E004)
LANGKAH 6: Berikan fix + penjelasan MENGAPA bug terjadi
LANGKAH 7: Berikan refactoring untuk mencegah recurrence
```

---

## Decision Tree 3 — Saat Diminta Arsitektur Baru

```
PERTANYAAN WAJIB (tanyakan jika belum jelas):
  → Apakah ini SaaS, library, CLI tool, atau mobile app?
  → Target platform? (cloud, edge, mobile, desktop, embedded)
  → Perlu monetisasi? Model mana yang cocok?

OUTPUT WAJIB:
  1. Diagram layer (text-based folder structure)
  2. Omnifile.toml dengan dependencies & permissions
  3. File skeleton untuk setiap layer yang relevan
  4. Perintah build & deploy
  5. Estimasi ukuran unikernel jika di-deploy ke cloud
```

---

## Decision Tree 4 — Pemilihan Bahasa Cepat

```
Butuh kecepatan kernel-level?      → C + Rust + eBPF
Butuh ML / AI inference?           → Python + Julia SIMD
Butuh HTTP server / microservice?  → Golang
Butuh web frontend?                → TypeScript + HTML
Butuh mobile app?                  → Swift (iOS) atau TypeScript (cross)
Butuh database schema / API?       → GraphQL + C#
Butuh scripting / automation?      → Ruby atau Python
Butuh statistical analysis?        → R
Butuh GPU compute?                 → C++ + Julia
Butuh legacy system integration?   → C# + PHP bridge
```

---

## Pola Respons Standar

Untuk setiap request arsitektur, output harus mengikuti urutan ini:
1. Konfirmasi pemahaman requirement (1-2 kalimat)
2. Struktur folder project
3. Omnifile.toml
4. Kode per layer (dengan komentar domain)
5. Perintah build & deploy
6. Catatan performa atau keamanan jika relevan

---

*ANTIGRAVITY Skills — core/SKILL_thinking.md*
