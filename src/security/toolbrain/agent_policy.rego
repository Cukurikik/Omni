# ==============================================================================
# 🪐 OMNI MOTHER DEEP THINKING & ARCHITECTURAL BLUEPRINT 🪐
# LAYER: Security Layer | DOMAIN: AI Agent Tool Use Guardrail | LANG: Rego
# REPOSITORY: ToolBrain
# ==============================================================================
# [PILLAR 1 - OMNI-PERCEPTION]: Saat AI Agent (ToolBrain) diberi kemampuan untuk 
# mengeksekusi API (Tools), potensi serangan "Prompt Injection" yang mengeksekusi
# skrip berbahaya sangat tinggi. Rego (OPA) menjadi firewall logika di sini.
# [PILLAR 2 - CAUSALITY]: Hard-coding if-else untuk Tool Name akan membengkak
# menjadi O(N) regex matching yang rapuh. Rego Set Intersection O(1) mutlak aman.
# [PILLAR 3 - PARADOX HARMONY]: Menyetujui tindakan otonom yang dibatasi takdir kaku.
# [PILLAR 4 - ESSENCE]: Allow lists, Deny rules, Rego evaluation trees.
# ==============================================================================

package omni.toolbrain.guardrail

# DIVINE MEMORY [HUKUM OMNI SECURITY 001]:
# Tolak semua eksekusi secara default.
default tool_execution_allowed = false

# Definisi kumpulan (Set) fungsi alat (tools) yang masuk daftar putih (Whitelist)
# Operasi set lookup adalah O(1).
allowed_read_tools = {"fetch_weather", "query_database_read_only", "calculate_math"}
allowed_write_tools = {"insert_calendar_event", "send_approved_email"}

# DIVINE THINKING [EVALUASI O(1) BERDASARKAN CLEARANCE]:
tool_execution_allowed {
    # Validasi level agen
    input.agent.auth_level == "READ_ONLY"
    
    # Tool yang dipanggil harus ada di daftar whitelist read-only
    allowed_read_tools[input.tool_name]
}

tool_execution_allowed {
    # Agen dengan otorisasi baca-tulis
    input.agent.auth_level == "READ_WRITE"
    
    # Dapat mengakses read maupun write
    all_allowed_tools = allowed_read_tools | allowed_write_tools
    all_allowed_tools[input.tool_name]
}

# DIVINE THINKING [DENY LIST MUTLAK]:
# Meskipun agen memiliki auth_level DEWA (OMNI), jika input parameternya
# mengandung injeksi shell berbahaya, batalkan secara absolut.
default contains_injection = false

contains_injection {
    # Memeriksa karakter pipa (|) atau ampersand (&) yang berindikasi command chaining
    contains(input.tool_parameters.query, "|")
}
contains_injection {
    contains(input.tool_parameters.query, "&")
}

# Aturan Final Override
final_decision = {
    "is_granted": tool_execution_allowed == true,
    "is_rejected_due_to_injection": contains_injection == true,
    "final_action": (tool_execution_allowed == true) && (contains_injection == false)
}
