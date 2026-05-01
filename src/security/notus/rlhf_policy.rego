# ==============================================================================
# 🪐 OMNI MOTHER DEEP THINKING & ARCHITECTURAL BLUEPRINT 🪐
# LAYER: Security & Policy | DOMAIN: RLHF Data Governance | LANG: Rego
# REPOSITORY: argilla-io/notus
# ==============================================================================
# [PILLAR 1 - OMNI-PERCEPTION]: Rego (Open Policy Agent) bertindak sebagai 
# Layer Sekuritas Terpisah (Decoupled Security Layer). Semua keputusan otorisasi 
# terkait dataset DPO (Direct Preference Optimization) RLHF dinilai di sini.
# [PILLAR 2 - CAUSALITY]: Jika logika sekuritas disisipkan ke dalam kode Python,
# bug pada Python dapat meloloskan data rahasia. Rego berjalan di mesin sandboxed 
# WebAssembly dengan kompleksitas evaluasi aturan O(1) deterministik.
# [PILLAR 3 - PARADOX HARMONY]: Deklaratif 100%, matematis untuk perizinan.
# [PILLAR 4 - ESSENCE]: Default deny, pattern matching rules, Set unions.
# ==============================================================================

package omni.notus.dpo.policy

# DIVINE MEMORY [DEFAULT SECURE PATTERN]:
# Hukum Pertama OMNI Security: Selalu mulai dari kegagalan.
# Akses membaca dataset RLHF secara eksplisit ditolak (false) hingga
# ada aturan spesifik yang membuktikan sebaliknya.
default allow_dataset_access = false

# DIVINE THINKING [AUTHORIZATION LOGIC & BIG-O EVALUATION]:
# Mesin OPA akan mengkompilasi aturan ini menjadi Tree.
# Pengecekan terjadi dalam O(1) lookup di dalam AST internal mereka.
allow_dataset_access {
    # 1. Pengecekan JWT Token Role
    input.user.role == "AI_RESEARCHER"
    
    # 2. Pengecekan Department
    input.user.department == "NOTUS_ALIGNMENT"
    
    # 3. Pengecekan Level Sensitivitas Dataset vs Clearance Pengguna
    # Clearance harus lebih besar atau sama dengan sensitivitas data.
    input.user.clearance_level >= input.dataset.sensitivity_level
}

# DIVINE THINKING [TOXICITY FILTER INJECTION]:
# Mencegah model fine-tuning dari mengkonsumsi dataset preference
# yang memiliki skor toksisitas melampaui batas OMNI Core (0.85).
# Mencegah RLHF Reward Model keracunan (Data Poisoning).
default safe_for_training = false

safe_for_training {
    input.dataset.type == "DPO_PREFERENCE"
    input.dataset.max_toxicity_score < 0.85
    input.dataset.contains_pii == false
}

# DIVINE THINKING [RETURN ENCAPSULATION]:
# Mengembalikan monad objek JSON agregat untuk diuraikan oleh Go API Gateway
training_clearance_manifest = {
    "access_granted": allow_dataset_access,
    "is_safe_for_compute": safe_for_training,
    "audit_timestamp": input.system.timestamp
}
