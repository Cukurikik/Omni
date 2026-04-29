# 🏗️🧱 SECTION 16 — UNIVERSAL BINARY & EXECUTABLE BUILDER

**ANTIGRAVITY MOTHER** tidak hanya menulis kode. Ia adalah **kompilator semesta** (universal compiler) yang dapat menghasilkan aplikasi siap pakai dalam **berbagai format executable dan installer** langsung dari source code multibahasa, tanpa memerlukan toolchain eksternal yang rumit. Seluruh proses—dari kompilasi, linking, optimasi, signing, hingga packaging—dilakukan secara otomatis oleh OMNI CLI dengan satu perintah.

### 16.1 — Daftar Target & Format yang Didukung

| Platform / Format         | Ekstensi                                        | Keterangan                              |
| :------------------------ | :---------------------------------------------- | :-------------------------------------- |
| **Windows**               | `.exe`, `.msi`, `.msix`                         | Native, installer, UWP                  |
| **Linux**                 | `.elf`, `.appimage`, `.deb`, `.rpm`, `.flatpak` | Binary native & package manager         |
| **macOS**                 | `.mach-o`, `.app`, `.pkg`, `.dmg`               | Bundle, installer, disk image           |
| **Android**               | `.apk`, `.aab`, `.so`                           | APK, Android App Bundle, native library |
| **iOS / iPadOS**          | `.ipa`, `.app`                                  | iPhone/iPad archive                     |
| **Web**                   | `.wasm`, `.html`, `.js`                         | WebAssembly & static site               |
| **Embedded / Bare Metal** | `.bin`, `.hex`, `.img`, `.uf2`                  | Firmware, microcontroller               |
| **Unikernel**             | `.ukl`                                          | OMNI Unikernel (3‑8MB)                  |
| **Library**               | `.dll`, `.so`, `.dylib`, `.a`, `.lib`           | Shared & static libraries               |
| **CLI / Server**          | binary tunggal tanpa ekstensi                   | Standalone untuk Linux/macOS            |
| **Plugin / Extension**    | `.wasm`, `.vst`, `.gdextension`                 | Plugin untuk aplikasi lain              |
| **Container**             | `.oci.tar`, `Dockerfile` (generated)            | OCI image / Docker                      |

### 16.2 — Build System Omni (Tanpa Toolchain Ketergantungan Eksternal)

OMNI CLI mengintegrasikan **LLVM‑Omni** dan cross‑compiler untuk semua target. Cukup tentukan target di `Omnifile.toml` atau di command line.

```toml
# Omnifile.toml
[build]
entry_point   = "src/main.omni"
targets       = ["x86_64‑windows", "aarch64‑macos", "aarch64‑android", "wasm32"]
optimize      = "release"
code_signing  = true
```

```bash
# Build semua target sekaligus
omni build --target all

# Build spesifik
omni build --target x86_64‑windows   # menghasilkan .exe
omni build --target aarch64‑android  # menghasilkan .apk
omni build --target wasm32           # menghasilkan .wasm + .html
omni build --target aarch64‑macos    # menghasilkan .app bundle
```

### 16.3 — Konfigurasi Build Per‑Target Lengkap

Setiap target bisa dikustomisasi secara detail, termasuk ikon, versi, permission, capabilities, dan signing identity.

```toml
[[build.target]]
name        = "x86_64‑windows"
type        = "executable"
output      = "./dist/MyApp.exe"
icon        = "./assets/icon.ico"
version     = "1.0.0"
sign        = { certificate = "codesign.pfx", algorithm = "sha256" }
permissions = ["net", "fs:./data/**"]

[[build.target]]
name        = "aarch64‑android"
type        = "apk"
output      = "./dist/MyApp.apk"
package_name = "com.example.myapp"
min_sdk     = 26
target_sdk  = 34
permissions = ["android.permission.INTERNET", "android.permission.CAMERA"]
sign        = { keystore = "release.keystore", alias = "myapp" }

[[build.target]]
name        = "aarch64‑macos"
type        = "appbundle"
output      = "./dist/MyApp.app"
bundle_id   = "com.example.myapp"
entitlements = ["com.apple.security.network.client"]
sign        = { developer_id = "Apple Developer ID" }

[[build.target]]
name        = "web"
type        = "wasm"
output      = "./dist/web/"
title       = "My App"
description = "Aplikasi web progresif"
features    = ["threads", "simd"]
```

### 16.4 — Cross‑Compile dari Satu Basis Kode 15+ Bahasa

Kode sumber multibahasa dianalisis oleh OMNI untuk menghasilkan kode native yang optimal per target. Tidak perlu rewrite per platform.

```omni
// src/main.omni — entry aplikasi lintas platform
fn main() {
  // UI layer akan dipilih otomatis sesuai target
  ui::launch(AppWindow {
    title: "Aplikasi Universal",
    content: DashboardComponent(),
  })
}

// src/ui/dashboard.ts — UI akan dirender native di setiap platform
component DashboardComponent() -> ts::JSX {
  return (
    <View>
      <Text>Halo dari OMNI</Text>
    </View>
  )
}
```

Saat build untuk Android, UI akan dirender dengan SwiftUI/Compose bridge; saat build untuk web, menjadi WASM+HTML; saat desktop, menjadi native window.

### 16.5 — Packaging & Installer Otomatis

Selain executable mentah, OMNI dapat menghasilkan installer profesional.

```bash
# Buat installer Windows (.msi)
omni package --type msi --output "MyAppInstaller.msi"

# Buat disk image macOS (.dmg)
omni package --type dmg --output "MyApp.dmg" --background "assets/dmg_bg.png"

# Buat AppImage Linux
omni package --type appimage --output "MyApp.AppImage"

# Buat APK Android (debug / release)
omni package --type apk --mode release

# Buat IPA untuk iOS (memerlukan konfigurasi Apple)
omni package --type ipa

# Buat OCI container image
omni package --type oci --output myapp:latest

# Buat installer Flatpak
omni package --type flatpak
```

### 16.6 — One‑Click Build untuk Semua Platform

```bash
# Menghasilkan SEMUA format dari project saat ini
omni build --universe

# Output direktori dist/ berisi:
# MyApp.exe, MyApp.msi, MyApp.msix
# MyApp.elf, MyApp.AppImage, MyApp.deb, MyApp.rpm
# MyApp.app, MyApp.pkg, MyApp.dmg
# MyApp.apk, MyApp.aab
# MyApp.wasm, index.html, MyApp.js
# MyApp.bin, MyApp.hex (embedded)
# MyApp.ukl (unikernel)
```

### 16.7 — Signing & Notarisasi Otomatis

Untuk distribusi di App Store, Play Store, atau lingkungan enterprise, OMNI menangani code signing dan notarisasi.

```toml
[build.code_signing]
# Windows
windows_pfx  = "certs/code.pfx"
windows_pass = "$WINDOWS_SIGN_PASS"
# macOS
macos_developer_id = "Developer ID Application: Nama (XXXX)"
macos_notary_profile = "notary-profile"
# Android
android_keystore = "release.keystore"
android_key_alias = "upload"
android_key_pass = "$ANDROID_KEY_PASS"
```

### 16.8 — Ekstensi File Lainnya

ANTIGRAVITY juga dapat menghasilkan format lain sesuai kebutuhan:

- **Database** : `.sqlite`, `.duckdb` (file database terinisialisasi)
- **Dokumentasi** : `.pdf`, `.html` (dokumen API, user guide)
- **Asset bundles** : `.zip`, `.tar.gz`, `.omniar` (arsip terstruktur)
- **Virtual machine** : `.ova`, `.vhd` (image VM)
- **Firmware** : `.uf2`, `.hex`, `.bin` (mikrokontroler)
- **Driver** : `.sys` (Windows), `.kext`/`.dext` (macOS)

Perintah untuk menghasilkan file non‑eksekutabel juga melalui `omni build` dengan target khusus.

```bash
omni build --target sqlite    # menghasilkan database kosong dengan schema
omni build --target docs-pdf  # menghasilkan dokumentasi PDF
```
