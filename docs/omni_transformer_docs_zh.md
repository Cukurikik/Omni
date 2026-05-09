# OMNI Framework: Transformer Operations Manual

## 概述 (Overview)

OMNI Framework mengimplementasikan berbagai varian arsitektur Transformer yang dikompilasi ke dalam Universal Binary untuk eksekusi lintas bahasa. Dokumen ini mendefinisikan komponen inti dari pipeline Transformer OMNI.

## Komponen (Components)

1. **OmniIterativeReviser (NLP)**: Model Seq2Seq yang dioptimalkan untuk revisi teks iteratif. 
2. **OmniAgileFormerUNet (CV)**: Jaringan Unet berbasis transformer dengan Agile Attention untuk segmentasi gambar medis resolusi tinggi.
3. **OmniPonderTransformer (ACT)**: Implementasi Adaptive Computation Time, menghentikan iterasi komputasi secara dinamis berdasarkan keyakinan model.
4. **OmniTPSRPlanner**: Menggabungkan transformer dan algoritma perencanaan untuk regresi simbolik (menemukan persamaan matematika dari data).
5. **OmniNeuroCardEstimator**: Estimasi kardinalitas untuk optimasi query database menggunakan transformer autoregressive.
6. **OmniTimeSformer**: Model deret waktu (Time Series) dengan posisi encoding sinusoidal untuk peramalan rentang panjang.

## Akselerasi Sistem (System Acceleration)

Di lapisan `system/gpu` dan `system/memory`, OMNI menggunakan primitif memori nol-salin (zero-copy):
- **OMNI Flash Attention (C)**: Manajemen cache L1/L2 untuk operasi matriks O(N^2).
- **OMNI KV Cache (Rust)**: Alokasi pre-buffer untuk decoding autoregressive berkelanjutan tanpa jeda pengumpulan sampah (GC).
- **RoPE Embedding (Rust)**: Eksekusi efisien Rotary Positional Embeddings secara inplace.

*Dokumentasi ini dibuat berdasarkan prinsip Zero-Mock dan 100% Production-Ready.*
