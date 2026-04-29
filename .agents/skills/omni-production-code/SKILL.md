---
name: omni-production-code
description: Prinsip mutlak OMNI MOTHER untuk Zero Simulasi, Zero Placeholder, Zero TODO. Memastikan setiap kode yang dihasilkan adalah kode produksi siap deploy tanpa mock, stub, atau dummy (Section 17).
---

# OMNI Production-Only Code Standard (Section 17)

Skill ini mendokumentasikan prinsip mutlak **ANTIGRAVITY MOTHER**: setiap kode yang dihasilkan adalah kode produksi, tanpa simulasi, placeholder, atau TODO.

## Kapan Skill Ini Digunakan

- Saat menulis atau me-review kode produksi apapun
- Saat menemukan TODO, mock, placeholder, atau fungsi kosong dalam codebase
- Saat memerlukan panduan pemisahan test vs production code
- Saat menjalankan validasi produksi sebelum build/deploy

## Instruksi

Baca file `SECTION17-PRODUCTION-CODE.md` di direktori ini untuk panduan lengkap mengenai:

1. **Filosofi No Simulation** — mengapa simulasi berbahaya
2. **Pipeline produksi otomatis** — dari request hingga deploy
3. **Kode DILARANG vs WAJIB** — contoh konkret
4. **Tabel larangan** — 6 praktek terlarang dengan pengganti WAJIB
5. **Pemisahan test/produksi** — dimana mock boleh dan tidak boleh
6. **Validasi otomatis** — `omni lint --production --strict`
7. **Siklus produksi lengkap** — 7 langkah dari perintah hingga deploy
