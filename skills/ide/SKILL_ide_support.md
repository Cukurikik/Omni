# SKILL: IDE SUPPORT & WORKSPACE INTELLIGENCE
**File:** `ide/SKILL_ide_support.md`  
**Layer:** IDE Integration

---

## IDE yang Didukung

| IDE | Extension/Plugin | Fitur |
|-----|-----------------|-------|
| **VS Code** | `omni-intellisense` | Syntax, IntelliSense, debug, refactor, git integration |
| **JetBrains** (IDEA, GoLand, PyCharm, dll) | `OMNI Language Pack` | Full IDE experience, inspections, quick fixes |
| **Neovim** | LSP via `mason.nvim` + `omnils` | LSP completion, diagnostics, formatting |
| **Zed** | OMNI Extension Registry | Native extension, tree-sitter grammar |
| **Cursor** | Built-in | AI-assisted OMNI completion |
| **Helix** | LSP + tree-sitter | Completion, diagnostics |
| **Emacs** | `omni-mode` via MELPA | Syntax, flycheck, company-mode |

---

## Instalasi Extension

### VS Code
```bash
# Via command palette
ext install omni-framework.omni-intellisense

# Via CLI
code --install-extension omni-framework.omni-intellisense
```

### Neovim (lazy.nvim)
```lua
{
  "williamboman/mason.nvim",
  config = function()
    require("mason").setup()
    require("mason-lspconfig").setup({
      ensure_installed = { "omnils" }
    })
  end
}
```

### JetBrains
```
Settings → Plugins → Marketplace → Cari "OMNI Language Pack" → Install
```

---

## Fitur Workspace Intelligence

Saat ANTIGRAVITY terhubung ke workspace IDE melalui Language Server Protocol (LSP), kemampuan berikut tersedia:

### Analisis Kode
```
omni scan
→ Membaca seluruh workspace
→ Membangun dependency graph lintas 15 bahasa
→ Melaporkan: layer violations, missing error handling, dead code
```

### Auto-Fix
```
omni fix --all
→ Memperbaiki semua E001-E005 secara otomatis
→ Menambahkan missing Result<> wrapper
→ Memindahkan kode yang salah layer ke layer yang benar
```

### Security Audit
```
omni audit
→ SAST (Static Application Security Testing)
→ Cek dependency vulnerabilities
→ Cek permission yang terlalu luas di Omnifile.toml
→ Cek secrets yang ter-hardcode di kode
```

### Refactoring
```
omni refactor --suggest
→ Mengidentifikasi fungsi yang bisa di-extract
→ Menyarankan pemilihan bahasa yang lebih tepat per domain
→ Mendeteksi bottleneck performa
```

---

## OMNI LSP Configuration (omnils)

```json
// .omni/lsp-config.json
{
  "omnils": {
    "enable_simd_hints": true,
    "strict_layer_check": true,
    "auto_doc_generation": true,
    "format_on_save": true,
    "max_diagnostics": 100,
    "languages": {
      "rust": { "edition": "2021" },
      "python": { "version": "3.12" },
      "typescript": { "strict": true },
      "julia": { "simd": true }
    }
  }
}
```

---

# SKILL: SEMUA PERINTAH CLI
**File:** `ide/SKILL_cli_commands.md`

---

## Referensi Lengkap OMNI CLI

### Project Management
```bash
omni new <name>                      # Buat project baru
omni new <name> --template <tmpl>    # Dengan template: hft, ml, saas, ui, api
omni init                            # Init OMNI di folder existing
omni info <package>                  # Info package dari OMNI-NEXUS
```

### Dependency Management
```bash
omni get <package>                   # Install package
omni get <package>@<version>         # Install versi spesifik
omni remove <package>                # Hapus package
omni update                          # Update semua dependencies
omni update <package>                # Update satu package
omni list                            # Daftar dependencies terinstall
omni tree                            # Dependency tree
```

### Code Quality
```bash
omni check                           # Validasi kode (cepat)
omni check --strict                  # Validasi ketat (semua rules)
omni fix                             # Fix issues otomatis
omni fix --all                       # Fix semua issues
omni fmt                             # Format kode
omni audit                           # Security audit
omni scan                            # Analisis lengkap workspace
omni refactor --suggest              # Saran refactoring
```

### Testing
```bash
omni test                            # Jalankan semua test
omni test --unit                     # Unit test saja
omni test --integration              # Integration test saja
omni test --filter <pattern>         # Filter test berdasarkan nama
omni test --all --coverage           # Test + coverage report
omni test --coverage-threshold 80    # Fail jika coverage < 80%
omni bench                           # Benchmark
omni bench --compare                 # Bandingkan dengan versi sebelumnya
```

### Build
```bash
omni build                           # Debug build
omni build --release                 # Release build
omni build --release --target all    # Semua platform
omni build --release --target wasm32 # Spesifik target
omni unikernel build                 # Build unikernel
omni unikernel build --target cloud  # Unikernel untuk cloud
omni clean                           # Hapus build artifacts
```

### Documentation
```bash
omni doc                             # Generate dokumentasi
omni doc --format openapi            # Format OpenAPI/Swagger
omni doc --format markdown           # Format Markdown
omni doc --serve --port 8080         # Serve lokal untuk preview
```

### Package Publishing
```bash
omni login                           # Login ke OMNI-NEXUS
omni logout                          # Logout
omni publish --dry-run               # Simulasi publish
omni publish                         # Publish ke registry
omni yank <pkg>@<ver> --reason "..." # Yank versi bermasalah
omni version patch/minor/major       # Bump versi
omni changelog generate              # Generate changelog dari git
omni tag <v>                         # Tag versi
omni stats <package>                 # Statistik download
```

### Cloud Deployment
```bash
omni cloud login                     # Login ke OMNI Cloud
omni cloud deploy <file.ukl>         # Deploy unikernel
omni cloud deploy <file.ukl> --region id-jkt-1  # Deploy ke region spesifik
omni cloud list                      # Daftar deployment aktif
omni cloud logs <app>                # Stream logs
omni cloud logs <app> --follow       # Follow logs real-time
omni cloud metrics <app>             # Metrik performa
omni cloud scale <app> --replicas 5  # Scale manual
omni cloud scale <app> --auto        # Auto-scale
omni cloud stop <app>                # Hentikan deployment
omni cloud delete <app>              # Hapus deployment
omni cloud regions                   # Daftar region tersedia
```

### Profile & Debug
```bash
omni profile                         # CPU profiling
omni profile --memory                # Memory profiling
omni profile --flamegraph            # Generate flamegraph SVG
omni debug                           # Attach debugger
```

---

*ANTIGRAVITY Skills — ide/SKILL_ide_support.md & SKILL_cli_commands.md*
