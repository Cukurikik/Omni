# ==============================================================================
# 🪐 OMNI MOTHER DEEP THINKING & ARCHITECTURAL BLUEPRINT 🪐
# LAYER: Security Layer | DOMAIN: Camera Stream Authentication | LANG: Rego
# REPOSITORY: camera
# ==============================================================================
# [PILLAR 1 - OMNI-PERCEPTION]: Akses langsung ke stream Kamera (Video Feed)
# sangat riskan. Rego memvalidasi token otentikasi JWT dari klien secara
# terpisah (decoupled) dari aplikasi Swift/PHP.
# [PILLAR 2 - CAUSALITY]: Logika otorisasi IF/ELSE di aplikasi rentan disalahpahami.
# Kebijakan OPA (Open Policy Agent) direpresentasikan sebagai tabel kebenaran logis
# yang tak terbantahkan O(1).
# [PILLAR 3 - PARADOX HARMONY]: Real-time streaming butuh pengamanan gerbang mati.
# [PILLAR 4 - ESSENCE]: Allow/Deny predicates, Token Claim evaluation.
# ==============================================================================

package omni.camera.auth

# DIVINE MEMORY [HUKUM OMNI SECURITY]:
# Default Deny untuk menutup port dari entitas asing.
default allow_stream_access = false

# DIVINE THINKING [JWT CLAIM VALIDATION]:
# Otorisasi diizinkan HANYA jika token sah DAN peran masuk whitelist DAN
# feed kamera yang dituju sama dengan izin akses di dalam token.
allow_stream_access {
    # 1. Pastikan klaim dasar valid (Mock: verifikasi JWT di-handle API proxy OMNI)
    input.token.is_valid == true
    
    # 2. Level izin memadai
    input.token.role == "SYSTEM_ADMIN"
}

allow_stream_access {
    input.token.is_valid == true
    input.token.role == "VISION_AI_AGENT"
    
    # 3. Validasi ID stream (Pencocokan Presisi)
    # Agen hanya bisa mengakses kamera tertentu, BUKAN global admin.
    input.token.allowed_camera_ids[_] == input.request.target_camera_id
}

# Rule helper untuk mendeteksi token kadaluarsa (Logical Constraint)
deny_expired_token {
    input.token.exp < input.request.current_time_epoch
}

# FINAL RESOLUTION OBJECT (Monadic Audit Trail)
# Proxy Gateway OMNI akan membaca struktur ini dan menolak request jika granted == false
authorization_decision = {
    "granted": allow_stream_access == true && deny_expired_token == false,
    "camera_id": input.request.target_camera_id,
    "audit_reason": "Camera OPA Ruleset v2.0"
}
