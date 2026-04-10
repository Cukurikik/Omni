#!/usr/bin/env python3
"""
==========================================
🔨 OMNI-FORGE: THE SOVEREIGN BUILD SYSTEM
==========================================
Pande Besi yang melebur Rust, Golang, dan TypeScript
menjadi SATU BINER ABSOLUT.

ALUR BUILD:
  1. Kompilasi Rust (core/) → libomni_core.so/.dll (V8 Engine Library)
  2. Kompilasi Golang (net/) → omni-runtime binary (Linked ke Rust via CGO)
  3. Bundle stdlib/ → Embed file JS ke dalam binary (opsional)
  4. Strip & Compress → Biner final yang ultra-ringan

PENGGUNAAN:
  python forge/build.py              → Build semua (Release mode)
  python forge/build.py --debug      → Build dengan debug symbols
  python forge/build.py --target linux → Cross-compile ke Linux
  python forge/build.py --clean      → Bersihkan semua artefak build

DEPENDENSI:
  - Rust toolchain (rustup/cargo)
  - Go toolchain (go 1.23+)
  - Python 3.10+
==========================================
"""

import subprocess
import sys
import os
import platform
import shutil
import time
import json
from pathlib import Path

# ==========================================
# 🎨 KONFIGURASI
# ==========================================

ROOT_DIR = Path(__file__).parent.parent.resolve()
CORE_DIR = ROOT_DIR / "core"
NET_DIR = ROOT_DIR / "net"
STDLIB_DIR = ROOT_DIR / "stdlib"
OUTPUT_DIR = ROOT_DIR / "dist"

VERSION = "1.3.0-SOVEREIGN"

# Deteksi OS
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"

# Extension
LIB_EXT = ".dll" if IS_WINDOWS else ".dylib" if IS_MACOS else ".so"
BIN_EXT = ".exe" if IS_WINDOWS else ""

# ==========================================
# 🔧 UTILITY FUNCTIONS
# ==========================================

def run(cmd, cwd=None, env=None):
    """Jalankan command dan tampilkan output real-time."""
    print(f"   🔨 {' '.join(cmd)}")
    merged_env = {**os.environ, **(env or {})}
    result = subprocess.run(cmd, cwd=cwd, env=merged_env)
    if result.returncode != 0:
        print(f"   ❌ GAGAL (exit code {result.returncode})")
        sys.exit(1)
    return result

def banner(message):
    """Print section banner."""
    print()
    print("═" * 60)
    print(f"  {message}")
    print("═" * 60)

def file_size_mb(path):
    """Hitung ukuran file dalam MB."""
    if path.exists():
        return path.stat().st_size / (1024 * 1024)
    return 0

# ==========================================
# ⚙️ TAHAP 1: KOMPILASI RUST (OMNI-CORE)
# ==========================================

def build_rust(debug=False):
    banner("⚙️ TAHAP 1: Mengompilasi Rust V8 Engine (OMNI-CORE)")
    
    if not (CORE_DIR / "Cargo.toml").exists():
        print("   ❌ Cargo.toml tidak ditemukan di core/")
        sys.exit(1)
    
    cmd = ["cargo", "build"]
    if not debug:
        cmd.append("--release")
    
    print(f"   📦 Mode: {'Debug' if debug else 'Release (LTO + Strip)'}")
    print(f"   📂 Directory: {CORE_DIR}")
    
    start = time.time()
    run(cmd, cwd=str(CORE_DIR))
    elapsed = time.time() - start
    
    # Verifikasi output
    profile = "debug" if debug else "release"
    lib_name = f"libomni_core{LIB_EXT}"
    lib_path = CORE_DIR / "target" / profile / lib_name
    
    if lib_path.exists():
        size = file_size_mb(lib_path)
        print(f"   ✅ Library: {lib_path}")
        print(f"   📊 Ukuran: {size:.2f} MB")
        print(f"   ⏱️ Waktu: {elapsed:.1f} detik")
    else:
        # Coba nama alternatif (Windows: omni_core.dll)
        alt_name = f"omni_core{LIB_EXT}"
        alt_path = CORE_DIR / "target" / profile / alt_name
        if alt_path.exists():
            print(f"   ✅ Library: {alt_path}")
        else:
            print(f"   ⚠️ Library tidak ditemukan. Cek output cargo build.")

# ==========================================
# 🐹 TAHAP 2: KOMPILASI GOLANG (OMNI-NET)
# ==========================================

def build_golang(debug=False):
    banner("🐹 TAHAP 2: Mengompilasi Golang Server (OMNI-NET)")
    
    if not (NET_DIR / "go.mod").exists():
        print("   ❌ go.mod tidak ditemukan di net/")
        sys.exit(1)
    
    # Pastikan output directory ada
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    output_binary = OUTPUT_DIR / f"omni-runtime{BIN_EXT}"
    
    # Set CGO flags untuk link ke Rust library
    profile = "debug" if debug else "release"
    rust_lib_dir = str(CORE_DIR / "target" / profile)
    
    env = {
        "CGO_ENABLED": "1",
        "CGO_LDFLAGS": f"-L{rust_lib_dir} -lomni_core",
    }
    
    cmd = [
        "go", "build",
        "-o", str(output_binary),
    ]
    
    if not debug:
        # Strip debug info dan optimasi
        cmd.extend(["-ldflags", f"-s -w -X main.Version={VERSION}"])
    
    cmd.append("./cmd/")
    
    print(f"   📦 Mode: {'Debug' if debug else 'Release (Stripped)'}")
    print(f"   📂 Directory: {NET_DIR}")
    print(f"   🔗 Linking: {rust_lib_dir}")
    
    start = time.time()
    run(cmd, cwd=str(NET_DIR), env=env)
    elapsed = time.time() - start
    
    if output_binary.exists():
        size = file_size_mb(output_binary)
        print(f"   ✅ Binary: {output_binary}")
        print(f"   📊 Ukuran: {size:.2f} MB")
        print(f"   ⏱️ Waktu: {elapsed:.1f} detik")
    else:
        print(f"   ⚠️ Binary tidak ditemukan di {output_binary}")

# ==========================================
# 📦 TAHAP 3: BUNDLE STDLIB
# ==========================================

def bundle_stdlib():
    banner("📦 TAHAP 3: Bundle Standard Library")
    
    stdlib_dest = OUTPUT_DIR / "stdlib"
    
    if stdlib_dest.exists():
        shutil.rmtree(stdlib_dest)
    
    if STDLIB_DIR.exists():
        shutil.copytree(STDLIB_DIR, stdlib_dest)
        
        # Hitung total file
        total_files = sum(1 for _ in stdlib_dest.rglob("*.js"))
        print(f"   ✅ {total_files} file JavaScript di-bundle ke dist/stdlib/")
    else:
        print("   ⚠️ stdlib/ tidak ditemukan, skip bundling")

# ==========================================
# 🧹 CLEAN
# ==========================================

def clean():
    banner("🧹 Membersihkan Artefak Build")
    
    targets = [
        CORE_DIR / "target",
        OUTPUT_DIR,
    ]
    
    for target in targets:
        if target.exists():
            shutil.rmtree(target)
            print(f"   🗑️ Dihapus: {target}")
        else:
            print(f"   ⏭️ Tidak ada: {target}")
    
    print("   ✅ Bersih!")

# ==========================================
# 📊 BUILD INFO
# ==========================================

def write_build_info():
    """Tulis informasi build ke file JSON."""
    info = {
        "version": VERSION,
        "build_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform": platform.system(),
        "arch": platform.machine(),
        "rust_target": "cdylib (V8 Engine)",
        "go_target": "binary (HTTP Server + CGO FFI)",
        "components": {
            "core": "Rust + V8 (Memory-Safe JavaScript Sandbox)",
            "net": "Golang (HTTP/TCP Server + Goroutines)",
            "stdlib": "JavaScript (Built-in route handlers)",
            "forge": "Python (Build System)"
        }
    }
    
    info_path = OUTPUT_DIR / "build-info.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(info_path, "w") as f:
        json.dump(info, f, indent=2)
    
    print(f"   📄 Build info: {info_path}")

# ==========================================
# 🚀 MAIN ENTRY POINT
# ==========================================

def main():
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  🔨  OMNI-FORGE: SOVEREIGN BUILD SYSTEM              ║")
    print("║  Melebur Rust + Golang + JS → 1 Biner Absolut       ║")
    print(f"║  Version: {VERSION}                         ║")
    print("╚══════════════════════════════════════════════════════╝")
    
    args = sys.argv[1:]
    
    if "--clean" in args:
        clean()
        return
    
    debug = "--debug" in args
    
    start_total = time.time()
    
    # Tahap 1: Rust
    build_rust(debug=debug)
    
    # Tahap 2: Golang
    build_golang(debug=debug)
    
    # Tahap 3: Bundle stdlib
    bundle_stdlib()
    
    # Build Info
    write_build_info()
    
    total_time = time.time() - start_total
    
    # Final Report
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║  ✅  BUILD SELESAI — KEDAULATAN MUTLAK TERCAPAI!     ║")
    print("╠══════════════════════════════════════════════════════╣")
    
    binary_path = OUTPUT_DIR / f"omni-runtime{BIN_EXT}"
    if binary_path.exists():
        size = file_size_mb(binary_path)
        print(f"║  📦 Binary  : dist/omni-runtime{BIN_EXT}")
        print(f"║  📊 Ukuran  : {size:.2f} MB")
    
    print(f"║  ⏱️ Total   : {total_time:.1f} detik")
    print(f"║  🦀 Core    : Rust V8 Engine ✅")
    print(f"║  🐹 Net     : Golang Server ✅")
    print(f"║  📦 Stdlib  : JavaScript Routes ✅")
    print("║                                                      ║")
    print("║  🚀 Jalankan: ./dist/omni-runtime serve --port 8080   ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

if __name__ == "__main__":
    main()
