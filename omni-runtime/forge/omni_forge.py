#!/usr/bin/env python3
"""
==========================================
🐍 OMNI-FORGE: THE CHIMERA BUILDER
==========================================
Pande Besi yang melebur Tiga Dimensi Bahasa
(C++, Rust, Golang) menjadi SATU BINER ABSOLUT.

Skrip ini hanya dijalankan oleh KITA (Pencipta OMNI)
saat merakit rilis biner, bukan oleh developer pengguna.

ALUR PELEBURAN:
  1. Rust + C++ (V8 Engine + SWC Transpiler) → libomni_core.a / .so / .dll
  2. Golang (Net + Syscall Bridge) → omni_engine binary (linked ke Rust via CGO)
  3. TypeScript stdlib → Dikompilasi menjadi JS dan di-bundle

EKSEKUSI:
  python forge/omni_forge.py              → Build Release
  python forge/omni_forge.py --debug      → Build Debug
  python forge/omni_forge.py --clean      → Bersihkan artefak
  python forge/omni_forge.py --target linux-amd64 → Cross-compile
==========================================
"""

import os
import subprocess
import sys
import platform
import shutil
import time
import json
from pathlib import Path

# ==========================================
# 🎨 KONSTANTAS
# ==========================================

VERSION = "1.3.0-SOVEREIGN"
CODENAME = "KEDAULATAN MUTLAK"

# Lokasi folder relatif dari lokasi script
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR.parent
CORE_DIR = BASE_DIR / "core"
NET_DIR = BASE_DIR / "net"
STDLIB_DIR = BASE_DIR / "stdlib"
RELEASE_DIR = BASE_DIR / "release"
DIST_DIR = BASE_DIR / "dist"

# Deteksi platform
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"

BIN_EXT = ".exe" if IS_WINDOWS else ""
LIB_PREFIX = "" if IS_WINDOWS else "lib"
LIB_EXT = ".dll" if IS_WINDOWS else ".dylib" if IS_MACOS else ".so"
STATIC_EXT = ".lib" if IS_WINDOWS else ".a"

# Cross-compilation targets
CROSS_TARGETS = {
    "linux-amd64":   {"GOOS": "linux",   "GOARCH": "amd64", "rust": "x86_64-unknown-linux-gnu"},
    "linux-arm64":   {"GOOS": "linux",   "GOARCH": "arm64", "rust": "aarch64-unknown-linux-gnu"},
    "darwin-amd64":  {"GOOS": "darwin",  "GOARCH": "amd64", "rust": "x86_64-apple-darwin"},
    "darwin-arm64":  {"GOOS": "darwin",  "GOARCH": "arm64", "rust": "aarch64-apple-darwin"},
    "windows-amd64": {"GOOS": "windows", "GOARCH": "amd64", "rust": "x86_64-pc-windows-msvc"},
}

# ==========================================
# 🔧 UTILITY FUNCTIONS
# ==========================================

class Colors:
    """ANSI color codes untuk terminal cantik."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_step(emoji, message):
    """Print formatted step message."""
    print(f"   {emoji} {message}")

def log_success(message):
    """Print success message."""
    print(f"   {Colors.GREEN}✅ {message}{Colors.END}")

def log_error(message):
    """Print error message."""
    print(f"   {Colors.RED}❌ {message}{Colors.END}")

def log_warning(message):
    """Print warning message."""
    print(f"   {Colors.YELLOW}⚠️ {message}{Colors.END}")

def run_cmd(cmd, cwd_path, step_name, env_extra=None):
    """Jalankan command dan tampilkan output real-time."""
    print(f"\n   🔨 {Colors.BOLD}{step_name}{Colors.END}")
    print(f"   📂 {cwd_path}")
    print(f"   💻 {' '.join(cmd)}")
    
    merged_env = {**os.environ, **(env_extra or {})}
    
    try:
        result = subprocess.run(
            cmd, 
            cwd=str(cwd_path), 
            check=True, 
            shell=False,
            env=merged_env,
            capture_output=False,
        )
        log_success(f"{step_name} — SELESAI!")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"[FATAL] {step_name} GAGAL! (exit code {e.returncode})")
        return False
    except FileNotFoundError:
        log_error(f"Command tidak ditemukan: {cmd[0]}")
        log_warning(f"Pastikan {cmd[0]} sudah terinstal di system PATH")
        return False

def file_size_human(path):
    """Format ukuran file."""
    if not path.exists():
        return "N/A"
    size = path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def check_toolchain():
    """Verifikasi semua tool yang dibutuhkan ada."""
    print("\n   🔍 Memeriksa Toolchain...\n")
    
    tools = {
        "rustc":  ["rustc", "--version"],
        "cargo":  ["cargo", "--version"],
        "go":     ["go", "version"],
        "python": [sys.executable, "--version"],
    }
    
    all_ok = True
    for name, cmd in tools.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            version = result.stdout.strip() or result.stderr.strip()
            log_success(f"{name}: {version}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            log_error(f"{name}: TIDAK DITEMUKAN!")
            all_ok = False
    
    return all_ok

# ==========================================
# ⚙️ TAHAP 1: TEMPA JANTUNG KINETIK (Rust + V8 + SWC)
# ==========================================

def forge_rust_core(debug=False, target=None):
    """Kompilasi Rust Core: V8 Engine + SWC Transpiler → Library."""
    
    if not (CORE_DIR / "Cargo.toml").exists():
        log_error("Cargo.toml tidak ditemukan di core/")
        sys.exit(1)
    
    cmd = ["cargo", "build"]
    
    if not debug:
        cmd.append("--release")
    
    if target:
        rust_target = CROSS_TARGETS.get(target, {}).get("rust")
        if rust_target:
            cmd.extend(["--target", rust_target])
    
    profile = "debug" if debug else "release"
    step_name = f"[1/3] Mengompilasi Rust V8 Engine + SWC Transpiler ({profile})"
    
    success = run_cmd(cmd, CORE_DIR, step_name)
    if not success:
        log_error("Peleburan Rust GAGAL! Proses dihentikan.")
        sys.exit(1)
    
    # Verifikasi output
    lib_name = f"{LIB_PREFIX}omni_core{LIB_EXT}"
    lib_path = CORE_DIR / "target" / profile / lib_name
    
    if lib_path.exists():
        log_step("📊", f"Library: {lib_path}")
        log_step("📊", f"Ukuran: {file_size_human(lib_path)}")
    else:
        log_warning(f"Library {lib_name} tidak ditemukan, cek output cargo")

# ==========================================
# 🐹 TAHAP 2: TEMPA JENDERAL GOLANG (Net + CGO Bridge)
# ==========================================

def forge_golang_net(debug=False, target=None):
    """Kompilasi Golang Server yang menyerap Rust Library via CGO."""
    
    if not (NET_DIR / "go.mod").exists():
        log_error("go.mod tidak ditemukan di net/")
        sys.exit(1)
    
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    
    bin_name = f"omni_engine{BIN_EXT}"
    output_path = RELEASE_DIR / bin_name
    
    # Rust library location
    profile = "debug" if debug else "release"
    rust_lib_dir = str(CORE_DIR / "target" / profile)
    
    # CGO flags untuk link ke Rust
    env_extra = {
        "CGO_ENABLED": "1",
    }
    
    # Cross-compilation env
    if target and target in CROSS_TARGETS:
        env_extra["GOOS"] = CROSS_TARGETS[target]["GOOS"]
        env_extra["GOARCH"] = CROSS_TARGETS[target]["GOARCH"]
    
    ldflags = f"-s -w -X main.Version={VERSION}"
    if debug:
        ldflags = f"-X main.Version={VERSION}-debug"
    
    cmd = [
        "go", "build",
        "-ldflags", ldflags,
        "-o", str(output_path),
        "./cmd/",
    ]
    
    step_name = f"[2/3] Mengompilasi Golang Server + Mengikat FFI Bridge"
    success = run_cmd(cmd, NET_DIR, step_name, env_extra)
    
    if not success:
        log_error("Peleburan Golang GAGAL!")
        sys.exit(1)
    
    if output_path.exists():
        log_step("📊", f"Binary: {output_path}")
        log_step("📊", f"Ukuran: {file_size_human(output_path)}")

# ==========================================
# ⚛️ TAHAP 3: BUNDLE STDLIB (TypeScript → JavaScript)
# ==========================================

def forge_stdlib():
    """Bundle TypeScript Standard Library ke dist."""
    step_name = "[3/3] Bundling OMNI Standard Library"
    print(f"\n   🔨 {Colors.BOLD}{step_name}{Colors.END}")
    
    stdlib_dest = DIST_DIR / "stdlib"
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    if stdlib_dest.exists():
        shutil.rmtree(stdlib_dest)
    
    if STDLIB_DIR.exists():
        shutil.copytree(STDLIB_DIR, stdlib_dest)
        
        ts_count = sum(1 for _ in stdlib_dest.rglob("*.ts"))
        js_count = sum(1 for _ in stdlib_dest.rglob("*.js"))
        
        log_success(f"Stdlib di-bundle: {ts_count} TypeScript + {js_count} JavaScript files")
    else:
        log_warning("stdlib/ tidak ditemukan, skip bundling")
    
    # Copy binary ke dist juga
    bin_name = f"omni_engine{BIN_EXT}"
    src_bin = RELEASE_DIR / bin_name
    dst_bin = DIST_DIR / bin_name
    
    if src_bin.exists():
        shutil.copy2(src_bin, dst_bin)
        log_success(f"Binary di-copy ke dist/")

# ==========================================
# 🧹 CLEAN
# ==========================================

def clean():
    """Bersihkan semua artefak build."""
    print(f"\n   🧹 {Colors.BOLD}Membersihkan Artefak Build...{Colors.END}")
    
    targets = [
        CORE_DIR / "target",
        RELEASE_DIR,
        DIST_DIR,
    ]
    
    for target in targets:
        if target.exists():
            shutil.rmtree(target)
            log_step("🗑️", f"Dihapus: {target.relative_to(BASE_DIR)}")
        else:
            log_step("⏭️", f"Tidak ada: {target.relative_to(BASE_DIR)}")
    
    log_success("Bersih total!")

# ==========================================
# 📊 WRITE BUILD MANIFEST
# ==========================================

def write_manifest():
    """Tulis manifest build ke JSON."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        "name": "OMNI-JS Runtime",
        "version": VERSION,
        "codename": CODENAME,
        "build_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "build_platform": f"{platform.system()}/{platform.machine()}",
        "python_version": platform.python_version(),
        "components": {
            "core": {
                "language": "Rust",
                "role": "V8 Engine + SWC Transpiler + Syscall Handler",
                "output": f"{LIB_PREFIX}omni_core{LIB_EXT}",
            },
            "net": {
                "language": "Golang",
                "role": "HTTP/TCP Server + Goroutines + CGO FFI Bridge",
                "output": f"omni_engine{BIN_EXT}",
            },
            "stdlib": {
                "language": "TypeScript",
                "role": "Developer API (omni/fs, omni/http, omni/crypto)",
                "modules": ["omni/fs", "omni/http", "omni/crypto"],
            },
            "forge": {
                "language": "Python",
                "role": "Build System (This script)",
            },
        },
        "node_js_required": False,
        "npm_required": False,
        "webpack_required": False,
    }
    
    manifest_path = DIST_DIR / "build-manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    log_step("📄", f"Manifest: {manifest_path}")

# ==========================================
# 🚀 MAIN: THE CHIMERA FORGE
# ==========================================

def forge_the_one_binary():
    """Peleburan Utama: 3 Bahasa → 1 Biner Absolut."""
    
    args = sys.argv[1:]
    
    # Parse flags
    debug = "--debug" in args
    do_clean = "--clean" in args
    target = None
    
    for arg in args:
        if arg.startswith("--target"):
            idx = args.index(arg)
            if idx + 1 < len(args):
                target = args[idx + 1]
    
    # Banner
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║  🐍  O M N I - F O R G E    v1.3.0                          ║")
    print("║  THE CHIMERA BUILDER — Pande Besi Kedaulatan Mutlak         ║")
    print("║                                                              ║")
    print("║  Melebur C++ (V8) + Rust (Safety) + Go (Net) → 1 Biner     ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    if do_clean:
        clean()
        return
    
    # Preflight check
    if not check_toolchain():
        log_error("Toolchain tidak lengkap! Install yang kurang dulu.")
        sys.exit(1)
    
    start_total = time.time()
    
    # ====== PELEBURAN ======
    print(f"\n{'═' * 60}")
    print(f"  🔥 MEMULAI PELEBURAN {'DEBUG' if debug else 'RELEASE'}")
    if target:
        print(f"  🎯 Target: {target}")
    print(f"{'═' * 60}")
    
    # Tahap 1: Rust Core (V8 + SWC + Syscalls)
    forge_rust_core(debug=debug, target=target)
    
    # Tahap 2: Golang Net (Server + CGO Bridge)
    forge_golang_net(debug=debug, target=target)
    
    # Tahap 3: Bundle Stdlib
    forge_stdlib()
    
    # Write Manifest
    write_manifest()
    
    # ====== LAPORAN AKHIR ======
    total_time = time.time() - start_total
    
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║  🌟  PELEBURAN SELESAI — BINER ABSOLUT TERCIPTAKAN!         ║")
    print("║                                                              ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    
    bin_path = RELEASE_DIR / f"omni_engine{BIN_EXT}"
    if bin_path.exists():
        print(f"║  📦 Binary    : release/omni_engine{BIN_EXT}")
        print(f"║  📊 Ukuran    : {file_size_human(bin_path)}")
    
    print(f"║  ⏱️ Waktu     : {total_time:.1f} detik")
    print(f"║  🦀 Rust Core : V8 Engine + SWC Transpiler ✅")
    print(f"║  🐹 Go Net    : HTTP Server + CGO Bridge ✅")
    print(f"║  ⚛️ Stdlib    : omni/fs · omni/http · omni/crypto ✅")
    print("║                                                              ║")
    print("║  🚀 JALANKAN:                                                ║")
    print(f"║     ./release/omni_engine{BIN_EXT} serve --port 3000         ║")
    print(f"║     ./release/omni_engine{BIN_EXT} run server.tsx             ║")
    print("║                                                              ║")
    print("║  📜 Node.js    : ❌ TIDAK DIBUTUHKAN                         ║")
    print("║  📜 npm        : ❌ TIDAK DIBUTUHKAN                         ║")
    print("║  📜 Webpack    : ❌ TIDAK DIBUTUHKAN                         ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

if __name__ == "__main__":
    forge_the_one_binary()
