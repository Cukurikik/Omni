#!/usr/bin/env node

import { execSync, spawn } from 'child_process';
import { existsSync, mkdirSync, writeFileSync, readFileSync, readdirSync, lstatSync, createWriteStream, openSync, unlinkSync, copyFileSync, rmSync } from 'fs';
import { join } from 'path';
import os from 'os';
import https from 'https';
import http from 'http';
import readline from 'readline';
import { locateOmnifile, parseOmnifile, toAppConfig, prettyPrintConfig, generateOmnifileContent } from '../lib/omnifile_parser.mjs';

// Mengambil perintah dari terminal (contoh: 'omni init my-app' -> args[0] = 'init', args[1] = 'my-app')
const args = process.argv.slice(2);
const command = args[0];
const projectName = args[1] || 'omni-project';

const ROOT_DIR = process.cwd();
const OMNI_BIN = join(ROOT_DIR, 'bin');

// Injeksi folder bin lokal ke PATH agar sistem bisa menemukannya
process.env.PATH = `${OMNI_BIN};${process.env.PATH}`;

// Pastikan folder bin ada
if (!existsSync(OMNI_BIN)) mkdirSync(OMNI_BIN, { recursive: true });

import { dirname } from 'path';

// ==========================================
// 🧬 THE GENESIS PROTOCOL: BLUEPRINT FILE INTI
// ==========================================
// Jika file-file ini hilang, OMNI akan menciptakannya dari ketiadaan
// lengkap dengan logika dasar, import, dan fungsinya.
const CORE_BLUEPRINTS = {
    // 1. Registry Backend (JSON)
    "configs/cli_registry.json": `{
  "tools": {
    "demo_tool": {
      "binary": "echo",
      "args": ["OMNI System is Online"],
      "timeout_mins": 1
    }
  }
}`,
    // 2. Registry Metadata (JSON)
    "configs/registry_omni.json": `{
  "tools": [
    {
      "id": "demo_tool",
      "category": "VIDEO",
      "name": "Alat Demo",
      "description": "Otomatis dibuat oleh sistem Genesis.",
      "endpoint": "/api/v1/tools/universal/execute",
      "accepts": "*/*",
      "delegateTo": "C++",
      "extraInputs": []
    }
  ]
}`,
    // 3. Map Frontend (TypeScript)
    "ui/src/configs/toolsMap.ts": `import { LucideIcon, Video, Mic, Image, FileText, ArrowRightLeft, Sparkles, Box, Bot } from 'lucide-react';

export type OmniCategory = 'VIDEO' | 'AUDIO' | 'IMAGE' | 'PDF' | 'CONVERTER' | 'AI' | 'LLM' | 'SYSTEM';

export interface OmniToolUI {
  id: string;
  name: string;
  description: string;
  category: OmniCategory;
  accepts: string;
  icon: LucideIcon;
  requiresInput?: { key: string; label: string; type: 'text' | 'password' }[];
  endpoint?: string;
  extraInputs?: any[];
}

export const OMNI_TOOLS_UI: OmniToolUI[] = [
  // @omni-gen-start
  { 
    id: 'demo_tool', 
    name: 'Alat Demo', 
    description: 'Otomatis dibuat oleh sistem.', 
    category: 'SYSTEM', 
    accepts: '*/*',
    icon: Box,
    endpoint: '/api/v1/tools/universal/execute',
    extraInputs: []
  },
  // @omni-gen-end
];`,
    // 4. Main Golang Gateway (Golang)
    "api/main.go": `package main
import (
\t"fmt"
\t"net/http"
)
func main() {
\tfmt.Println("🛡️ OMNI GATEWAY ACTIVE ON PORT 8080")
\thttp.ListenAndServe(":8080", nil)
}`,
    // 5. Folder Karantina & Cache (Direktori Kosong dengan file .gitkeep)
    "release/omni_quarantine/.gitkeep": "",
    "release/omni_cache/.gitkeep": ""
};

// ==========================================
// 🏗️ MESIN PENCIPTA & PEMULIH (SELF-HEALING)
// ==========================================
function enforceGenesisProtocol() {
    let wasRepaired = false;

    console.log("🔍 [PRE-FLIGHT CHECK] Memeriksa integritas struktur folder dan file...");

    for (const [relativePath, defaultContent] of Object.entries(CORE_BLUEPRINTS)) {
        const fullPath = join(ROOT_DIR, relativePath);
        const dirPath = dirname(fullPath);

        if (!existsSync(fullPath)) {
            // 1. BUAT FOLDER JIKA TIDAK TERSEDIA (recursive: true mencegah error parent folder)
            if (!existsSync(dirPath)) {
                mkdirSync(dirPath, { recursive: true });
                console.log(`📁 DIBUAT: Direktori pelindung -> ${dirPath}`);
            }

            // 2. BUAT FILE & ISI KODE SESUAI FUNGSI/LOGIKA
            writeFileSync(fullPath, defaultContent, 'utf8');
            console.log(`✨ DIBUAT: File inti -> ${relativePath}`);
            wasRepaired = true;
        }
    }

    // 3. JIKA FILE SUDAH TERBUAT > BERIKAN INFO RERUN OTOMATIS
    if (wasRepaired) {
        console.log("\n🔄 [SYSTEM RECOVERY] OMNI telah memperbaiki struktur yang hilang/rusak.");
        console.log("🚀 Melanjutkan eksekusi perintah utama...\n");
    } else {
        console.log("✅ Integritas sistem 100%. Tidak ada file yang hilang.\n");
    }
}

console.log("=========================================");
console.log("⚡ OMNI TOOLS CLI v3.0 - OMNI-SPHERE Active");
console.log("=========================================\n");

// SELALU JALANKAN PROTOKOL PENCIPTAAN SEBELUM MELAKUKAN APAPUN!
// Ini menjamin command di bawahnya tidak akan pernah error karena file hilang.
enforceGenesisProtocol(); 

// ==========================================
// 🔫 THE PORT EXORCIST: ZOMBIE PROCESS KILLER
// ==========================================
function liberatePort(port, serviceName) {
    console.log(`🔍 [PORT SWEEPER] Memeriksa Jalur Komunikasi ${serviceName} (Port ${port})...`);
    
    try {
        if (os.platform() === 'win32') {
            // Windows: netstat -ano | findstr :PORT
            const cmd = `netstat -ano | findstr :${port}`;
            let output = "";
            try {
                output = execSync(cmd).toString().trim();
            } catch (e) {
                // Command returns exit code 1 if no process found - this is normal
                console.log(`✅ Port ${port} bersih dan aman dari gangguan.`);
                return;
            }

            if (output) {
                const lines = output.split('\n');
                lines.forEach(line => {
                    const parts = line.trim().split(/\s+/);
                    const pid = parts[parts.length - 1]; // PID is the last column in 'ano'
                    if (pid && !isNaN(pid) && pid !== '0') {
                        console.log(`⚠️ ANOMALI: Port ${port} disandera oleh Zombie [PID: ${pid}].`);
                        console.log(`🔫 Mengeksekusi Protokol Eliminasi (taskkill)...`);
                        try {
                            execSync(`taskkill /F /PID ${pid}`, { stdio: 'ignore' });
                            console.log(`💀 Zombie [${pid}] berhasil dimusnahkan!`);
                        } catch (e) {
                            console.log(`⚠️ Gagal mematikan proses ${pid}. Butuh hak akses administrator?`);
                        }
                    }
                });
                console.log(`✅ Port ${port} berhasil direbut kembali.`);
            }
        } else {
            // UNIX: lsof -t -i:PORT
            try {
                const pids = execSync(`lsof -t -i:${port}`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'] }).trim();
                if (pids) {
                    const pidArray = pids.split('\n');
                    console.log(`⚠️ ANOMALI: Port ${port} disandera oleh Zombie [PID: ${pidArray.join(', ')}].`);
                    pidArray.forEach(pid => {
                        execSync(`kill -9 ${pid}`);
                        console.log(`💀 Zombie [${pid}] berhasil dimusnahkan!`);
                    });
                }
            } catch (e) {
                console.log(`✅ Port ${port} bersih.`);
            }
        }
    } catch (error) {
        console.log(`✅ Jalur ${port} siap digunakan.`);
    }
}

// ==========================================
// 🚀 MAIN ENGINE: OMNI-RESONANCE DEV SERVER
// Golang sebagai Master Gateway tunggal.
// esbuild + Tailwind sebagai kompilator instan.
// OMNI-SIGHT sebagai detektor perubahan.
// WebSocket RESONANCE sebagai jaringan saraf.
// ==========================================
async function startDevServer() {
    console.log("\n==========================================");
    console.log("📡 OMNI-RESONANCE DEV SERVER — IGNITION");
    console.log("==========================================");
    console.log("   Server    : Golang Gateway (Port 3000)");
    console.log("   Compiler  : esbuild (incremental watch)");
    console.log("   CSS       : Tailwind CLI (watch mode)");
    console.log("   Watcher   : OMNI-SIGHT (chokidar)");
    console.log("   Reload    : OMNI-RESONANCE (WebSocket)");
    console.log("   Vite      : ☠️  ERADICATED");
    console.log("==========================================\n");

    // 0. BEBASKAN PORT
    console.log("🔓 Membebaskan jalur komunikasi...");
    liberatePort(3000, "Golang OMNI Gateway");

    // 1. KOMPILASI AWAL — Build UI ke release/public untuk Golang serve
    console.log("\n🏭 [STEP 1/4] Kompilasi awal via OMNI-COMPILER...");
    const releasePublicDir = join(ROOT_DIR, 'release', 'public');
    if (!existsSync(releasePublicDir)) mkdirSync(releasePublicDir, { recursive: true });
    
    try {
        execSync('node scripts/omni_compiler.mjs', { cwd: join(ROOT_DIR, 'ui'), stdio: 'inherit' });
    } catch (err) {
        console.error("❌ Kompilasi awal gagal. Perbaiki error sebelum melanjutkan.");
        process.exit(1);
    }

    // 2. SUNTIK RESONANCE SCRIPT ke index.html hasil build (untuk dev mode)
    console.log("\n💉 [STEP 2/4] Menyuntik Saraf OMNI-RESONANCE ke HTML...");
    const htmlPath = join(releasePublicDir, 'index.html');
    if (existsSync(htmlPath)) {
        let html = readFileSync(htmlPath, 'utf8');
        const resonanceScript = `
<!-- 📡 OMNI-RESONANCE: Live Reload Nerve (Dev Mode Only) -->
<script>
    (() => {
        let reconnectAttempts = 0;
        function connectResonance() {
            const ws = new WebSocket('ws://' + location.hostname + ':3000/ws/omni_live');
            ws.onopen = () => {
                reconnectAttempts = 0;
                console.log('%c📡 [OMNI-RESONANCE] Jaringan Saraf Terhubung.', 'color: #00ff88; font-weight: bold;');
            };
            ws.onmessage = (e) => {
                if (e.data === 'RELOAD_SIGNAL') {
                    console.log('%c🔄 [OMNI-RESONANCE] Kode berubah! Me-refresh...', 'color: #ffaa00; font-weight: bold;');
                    location.reload();
                }
            };
            ws.onclose = () => {
                reconnectAttempts++;
                const delay = Math.min(reconnectAttempts * 1000, 5000);
                console.log('%c📡 [RESONANCE] Terputus. Reconnect dalam ' + (delay/1000) + 's...', 'color: #ff4444;');
                setTimeout(connectResonance, delay);
            };
        }
        connectResonance();
    })();
</script>`;
        if (!html.includes('OMNI-RESONANCE')) {
            html = html.replace('</body>', resonanceScript + '\n</body>');
            writeFileSync(htmlPath, html);
            console.log("   ✅ Saraf RESONANCE berhasil disuntikan.");
        } else {
            console.log("   ✅ Saraf RESONANCE sudah tertanam.");
        }
    }

    // 3. NYALAKAN GOLANG GATEWAY (Port 3000 — Master tunggal)
    console.log("\n🐹 [STEP 3/4] Menyalakan Golang Gateway (Port 3000)...");
    const apiProcess = spawn('go', ['run', 'main.go'], { 
        cwd: join(ROOT_DIR, 'api'), 
        stdio: 'inherit', 
        shell: true 
    });

    // Tunggu Golang siap sebelum memulai file watcher
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 4. OMNI-SIGHT: Mata Radar yang tidak pernah berkedip
    console.log("\n👁️ [STEP 4/4] OMNI-SIGHT Aktif — Memantau setiap perubahan kode...");
    
    // Dynamic import chokidar (sudah di devDependencies ui/)
    const { default: chokidar } = await import('chokidar');
    
    let isRebuilding = false;
    let pendingRebuild = false;

    const triggerRebuild = async (changedPath) => {
        if (isRebuilding) {
            pendingRebuild = true;
            return;
        }
        isRebuilding = true;

        const shortPath = changedPath.replace(ROOT_DIR, '').replace(/\\\\/g, '/');
        console.log(`\n📝 [OMNI-SIGHT] Perubahan: ${shortPath}`);
        console.log("⚡ Re-kompilasi kilat...");

        const rebuildStart = Date.now();

        try {
            execSync('node scripts/omni_compiler.mjs', { 
                cwd: join(ROOT_DIR, 'ui'), 
                stdio: 'pipe' // Tidak spam console saat rebuild
            });

            const elapsed = ((Date.now() - rebuildStart) / 1000).toFixed(2);
            console.log(`✅ Re-kompilasi selesai dalam ${elapsed}s`);

            // Re-inject Resonance script (karena compiler menimpa index.html)
            if (existsSync(htmlPath)) {
                let html = readFileSync(htmlPath, 'utf8');
                if (!html.includes('OMNI-RESONANCE')) {
                    html = html.replace('</body>', resonanceScript + '\n</body>');
                    writeFileSync(htmlPath, html);
                }
            }

            // Kirim sinyal RELOAD ke Golang → Browser
            try {
                await fetch('http://localhost:3000/api/internal/trigger-reload');
                console.log("📡 Sinyal RELOAD dikirim ke browser.");
            } catch (_) {
                // Gateway belum siap, abaikan
            }
        } catch (err) {
            console.error("❌ Re-kompilasi gagal:", err.stderr?.toString()?.slice(0, 500) || err.message);
        }

        isRebuilding = false;

        if (pendingRebuild) {
            pendingRebuild = false;
            triggerRebuild(changedPath);
        }
    };

    const watcher = chokidar.watch([
        join(ROOT_DIR, 'ui', 'src'),
        join(ROOT_DIR, 'configs')
    ], { 
        ignoreInitial: true,
        awaitWriteFinish: { stabilityThreshold: 300, pollInterval: 100 },
        ignored: [/node_modules/, /\.git/, /dist/]
    });

    watcher.on('change', triggerRebuild);
    watcher.on('add', triggerRebuild);

    console.log("\n==========================================");
    console.log("🌟 OMNI-RESONANCE AKTIF!");
    console.log("==========================================");
    console.log("🚀 SEMUA LAYANAN BERJALAN DI: http://localhost:3000");
    console.log("📱 AKSES LOKAL (HP/LAN)    : http://0.0.0.0:3000");
    console.log("📡 WebSocket Live-Reload   : ws://localhost:3000/ws/omni_live");
    console.log("👁️  File Watcher            : ui/src + configs/");
    console.log("==========================================");
    console.log("Tekan CTRL+C untuk mematikan semua mesin.\n");

    // GRACEFUL SHUTDOWN
    process.on('SIGINT', () => {
        console.log("\n🛑 Mematikan OMNI-RESONANCE...");
        watcher.close();
        apiProcess.kill();
        process.exit();
    });

    apiProcess.on('exit', (code) => {
        if (code !== null && code !== 0) {
            console.error(`\n🚨 Golang Gateway mati dengan kode ${code}. Periksa error di atas.`);
        }
    });
}

// ==========================================
// 👻 OMNI DAEMON: BACKGROUND PROCESS MANAGER
// Server produksi yang menolak untuk mati.
// ==========================================
function runOmniDaemon() {
    console.log("\n==========================================" );
    console.log("👻 OMNI DAEMON — BACKGROUND PROCESS MANAGER");
    console.log("==========================================\n");

    // 1. Pastikan binary sudah di-build!
    const binaryExt = os.platform() === 'win32' ? '.exe' : '';
    const binaryName = `omni-gateway${binaryExt}`;
    const gatewayPath = join(ROOT_DIR, 'release', 'bin', binaryName);
    const pidPath = join(ROOT_DIR, 'release', 'omni.pid');

    if (!existsSync(gatewayPath)) {
        console.log("❌ [FATAL] Binary omni-gateway tidak ditemukan!");
        console.log(`   Path yang dicari: ${gatewayPath}`);
        console.log("💡 Jalankan 'omni build' terlebih dahulu sebelum memanggil Daemon.");
        process.exit(1);
    }

    // 2. Cek apakah daemon sudah berjalan
    if (existsSync(pidPath)) {
        const existingPid = readFileSync(pidPath, 'utf8').trim();
        try {
            process.kill(parseInt(existingPid), 0); // Signal 0 = cek hidup
            console.log(`⚠️  OMNI Daemon SUDAH berjalan (PID: ${existingPid}).`);
            console.log("💡 Gunakan 'omni stop' untuk menghentikan, lalu 'omni start' untuk memulai ulang.");
            return;
        } catch (_) {
            // PID sudah mati, bersihkan file lama
            unlinkSync(pidPath);
        }
    }

    // 3. Siapkan Log Files
    const releaseDir = join(ROOT_DIR, 'release');
    if (!existsSync(releaseDir)) mkdirSync(releaseDir, { recursive: true });
    const outLog = openSync(join(releaseDir, 'omni-out.log'), 'a');
    const errLog = openSync(join(releaseDir, 'omni-err.log'), 'a');

    // 4. Panggil Roh Server secara Terpisah (Detached)
    const daemonProcess = spawn(gatewayPath, [], {
        cwd: join(ROOT_DIR, 'release', 'bin'),
        detached: true,              // KUNCI: Putuskan dari terminal!
        stdio: ['ignore', outLog, errLog]
    });

    // 5. Putuskan Tali Pusar
    daemonProcess.unref();

    // 6. Simpan PID
    writeFileSync(pidPath, daemonProcess.pid.toString());

    console.log("✅ [STATUS: IMMORTAL] OMNI Gateway telah lepas landas!\n");
    console.log(`🧬 Process ID (PID) : \x1b[32m${daemonProcess.pid}\x1b[0m`);
    console.log(`🌐 Endpoint         : http://0.0.0.0:3000`);
    console.log(`📂 Log Aktivitas    : release/omni-out.log`);
    console.log(`📂 Log Error        : release/omni-err.log`);
    console.log(`📂 PID File         : release/omni.pid`);
    console.log(`\n\x1b[33mAnda sekarang bisa MENUTUP IDE dan TERMINAL ini dengan aman.\x1b[0m`);
    console.log("Server OMNI akan terus hidup dan melayani port 3000 di latar belakang.\n");
}

function stopOmniDaemon() {
    console.log("\n🛑 [OMNI DAEMON] Menjalankan Protokol Eliminasi...");
    const pidPath = join(ROOT_DIR, 'release', 'omni.pid');

    if (!existsSync(pidPath)) {
        console.log("⚠️  Tidak ada daemon yang sedang berjalan (file PID tidak ditemukan).");
        return;
    }

    const pid = readFileSync(pidPath, 'utf8').trim();

    try {
        // Coba graceful kill dulu (SIGTERM)
        if (os.platform() === 'win32') {
            execSync(`taskkill /PID ${pid} /F`, { stdio: 'pipe' });
        } else {
            process.kill(parseInt(pid), 'SIGTERM');
        }
        console.log(`💀 Proses [PID: ${pid}] berhasil dihentikan.`);
    } catch (e) {
        console.log(`⚠️  Proses [PID: ${pid}] sudah mati atau tidak ditemukan.`);
    }

    // Bersihkan file PID
    try { unlinkSync(pidPath); } catch (_) {}
    console.log("✅ Daemon berhenti. Port 3000 telah dibebaskan.\n");
}

function statusOmniDaemon() {
    console.log("\n📡 [OMNI DAEMON] Status Check...");
    const pidPath = join(ROOT_DIR, 'release', 'omni.pid');

    if (!existsSync(pidPath)) {
        console.log("⚪ Status: TIDAK AKTIF (daemon tidak berjalan)\n");
        return;
    }

    const pid = readFileSync(pidPath, 'utf8').trim();

    try {
        process.kill(parseInt(pid), 0); // Signal 0 = cek hidup
        console.log(`🟢 Status: AKTIF (IMMORTAL)`);
        console.log(`🧬 PID    : ${pid}`);
        console.log(`🌐 Server : http://0.0.0.0:3000`);

        // Tampilkan 10 baris terakhir log
        const outLogPath = join(ROOT_DIR, 'release', 'omni-out.log');
        if (existsSync(outLogPath)) {
            const logContent = readFileSync(outLogPath, 'utf8');
            const lastLines = logContent.split('\n').slice(-10).join('\n');
            console.log(`\n📋 Log Terakhir:\n${lastLines}`);
        }
        console.log();
    } catch (_) {
        console.log(`🔴 Status: MATI (PID ${pid} sudah tidak ada)`);
        try { unlinkSync(pidPath); } catch (_) {}
        console.log("   File PID telah dibersihkan.\n");
    }
}
// ==========================================
// 🔄 OMNI-SYNC: THE AUTO-ROUTER GENERATOR
// ==========================================
// Membaca registry JSON dan menghasilkan kode Golang (registry.go)
// agar Backend sinkron tanpa perlu edit manual.
function generateGoRegistry() {
    console.log("🔄 [OMNI-SYNC] Menghasilkan Router Golang (api/engine/registry.go)...");
    
    const registryPath = join(ROOT_DIR, 'configs', 'cli_registry.json');
    const outputPath = join(ROOT_DIR, 'api', 'engine', 'registry.go');
    
    if (!existsSync(registryPath)) {
        console.error("❌ Registry JSON tidak ditemukan!");
        return;
    }

    const registry = JSON.parse(readFileSync(registryPath, 'utf8'));
    const tools = registry.tools;
    
    let goCode = `package engine

import (
\t"fmt"
\t"omnitools/core"
\t"omnitools/services"
)

// ExecuteTool adalah Switchboard utama yang dihasilkan otomatis oleh OMNI-SYNC.
// JANGAN EDIT FILE INI SECARA MANUAL!
func ExecuteTool(job *core.Job) ([]byte, error) {
\tswitch job.ID {
`;

    for (const [id, config] of Object.entries(tools)) {
        if (id.startsWith('=') || id.startsWith('_')) continue;
        
        // Bersihkan ID untuk nama fungsi jika perlu, tapi di sini kita pakai string match
        goCode += `\tcase "${id}":
\t\treturn services.ExecuteEngineWithTimeout(job.EngineCmd, job.Args, job.Timeout)
`;
    }

    goCode += `\tdefault:
\t\treturn nil, fmt.Errorf("tool_id [%s] tidak terdaftar di engine registry", job.EngineCmd)
\tdefault:
\t\treturn nil, fmt.Errorf("tool ID tidak dikenali: %s", job.ID)
\t}
}
`;

    // Pastikan folder engine ada
    const engineDir = dirname(outputPath);
    if (!existsSync(engineDir)) mkdirSync(engineDir, { recursive: true });

    writeFileSync(outputPath, goCode, 'utf8');
    console.log("✅ [OMNI-SYNC] Registry Golang berhasil diperbarui!");
}

// ==========================================
// 📖 OMNI-DOCS: API DOCUMENTATION GENERATOR
// ==========================================
function generateOmniDocs() {
    console.log("📖 [OMNI-DOCS] Memindai seluruh artefak kode...");
    
    const registry = JSON.parse(readFileSync(join(ROOT_DIR, 'configs', 'cli_registry.json'), 'utf8'));
    const appConfig = JSON.parse(readFileSync(join(ROOT_DIR, 'configs', 'appconfig.json'), 'utf8'));

    const docsData = {
        project: appConfig.app_name,
        version: appConfig.version,
        baseUrl: `http://localhost:${appConfig.server.port}/api/v1`,
        endpoints: []
    };

    // Otomatis memetakan 150+ fitur dari registry ke dokumentasi API
    for (const [id, cfg] of Object.entries(registry.tools)) {
        docsData.endpoints.push({
            id: id,
            name: id.replace(/_/g, ' ').toUpperCase(),
            description: cfg.description,
            method: "POST",
            path: `/omni/execute?tool_id=${id}`,
            headers: {
                "X-OMNI-KEY": "Your_API_Key_Here",
                "Content-Type": "multipart/form-data"
            },
            params: cfg.params || ["file"]
        });
    }

    // Tulis ke folder public agar bisa diakses browser
    const releasePublicDir = join(ROOT_DIR, 'release', 'public');
    if (!existsSync(releasePublicDir)) mkdirSync(releasePublicDir, { recursive: true });
    
    const docsPath = join(releasePublicDir, 'omni_docs.json');
    writeFileSync(docsPath, JSON.stringify(docsData, null, 2));
    console.log("✅ [OMNI-DOCS] Metadata berhasil diekstrak ke omni_docs.json");
}

// ==========================================
// 🛡️ OMNI-IMMORTALITY: KERNEL SERVICE GENERATOR
// ==========================================
// Mendaftarkan OMNI Gateway sebagai Systemd Service di Linux.
// Ini membuat OS Linux bertanggung jawab penuh atas kehidupan proses:
// - Auto-start saat server boot
// - Auto-restart dalam 3 detik setelah crash
// - Log terintegrasi ke journalctl
// - Zero downtime bahkan setelah hard reboot
// ==========================================
function generateSystemdService() {
    console.log("\n🛡️ [OMNI-IMMORTALITY] Membuat Surat Kuasa Kernel (Systemd Service)...");

    const appConfigPath = join(ROOT_DIR, 'configs', 'appconfig.json');
    const appConfig = existsSync(appConfigPath)
        ? JSON.parse(readFileSync(appConfigPath, 'utf8'))
        : { app_name: 'Omni', version: '2.0.0' };

    // Nama service di Linux (hilangkan spasi, huruf kecil)
    const serviceName = appConfig.app_name.replace(/\s+/g, '-').toLowerCase() + '-framework';
    const binaryPath = join(ROOT_DIR, 'release', 'bin', 'omni_gateway');
    const workingDir = join(ROOT_DIR, 'release', 'bin');

    // 1. Tulis konfigurasi Systemd murni
    const serviceContent = `[Unit]
Description=${appConfig.app_name} v${appConfig.version || '2.0.0'} — High-Performance Gateway (OMNI Framework)
Documentation=https://github.com/omni-tools/framework
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=${workingDir}
ExecStart=${binaryPath}
Restart=always
RestartSec=3
LimitNOFILE=65536
LimitNPROC=4096

# Environment variables
Environment=OMNI_ENV=production
Environment=OMNI_ROOT=${ROOT_DIR}

# Resource Protection (Hardening)
ProtectHome=true
ProtectSystem=strict
ReadWritePaths=${ROOT_DIR}/release
NoNewPrivileges=true

# Logging — Mengarahkan langsung ke sistem jurnal Linux (journalctl)
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${serviceName}

# Graceful shutdown timeout
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
`;

    const releaseDir = join(ROOT_DIR, 'release');
    if (!existsSync(releaseDir)) mkdirSync(releaseDir, { recursive: true });

    const serviceFilePath = join(releaseDir, `${serviceName}.service`);
    writeFileSync(serviceFilePath, serviceContent);

    // 2. Generate skrip instalasi otomatis
    const installScript = `#!/bin/bash
# ============================================
# 🛡️ OMNI-IMMORTALITY AUTO-INSTALLER
# Jalankan: sudo bash release/install-service.sh
# ============================================
set -e

SERVICE_NAME="${serviceName}"
SERVICE_FILE="${serviceFilePath}"
SYSTEMD_DIR="/etc/systemd/system"

echo "🛡️ [OMNI-IMMORTALITY] Mendaftarkan $SERVICE_NAME ke Kernel Linux..."

# 1. Copy service file ke systemd
cp "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME.service"
echo "   ✅ Service file disalin ke $SYSTEMD_DIR/"

# 2. Reload systemd daemon
systemctl daemon-reload
echo "   ✅ Systemd daemon di-reload"

# 3. Enable auto-start on boot
systemctl enable $SERVICE_NAME
echo "   ✅ Auto-start saat boot AKTIF"

# 4. Start service sekarang
systemctl start $SERVICE_NAME
echo "   ✅ Service dimulai"

# 5. Tampilkan status
echo ""
echo "=========================================="
echo "🟢 OMNI GATEWAY SEKARANG IMMORTAL!"
echo "=========================================="
systemctl status $SERVICE_NAME --no-pager
echo ""
echo "📋 Perintah berguna:"
echo "   journalctl -u $SERVICE_NAME -f     → Log real-time"
echo "   systemctl restart $SERVICE_NAME     → Restart"
echo "   systemctl stop $SERVICE_NAME        → Stop"
echo "   systemctl disable $SERVICE_NAME     → Matikan auto-start"
echo "=========================================="
`;

    const installScriptPath = join(releaseDir, 'install-service.sh');
    writeFileSync(installScriptPath, installScript);

    // 3. Generate PM2 ecosystem file (fallback untuk non-root)
    const pm2Ecosystem = {
        apps: [{
            name: serviceName,
            script: binaryPath,
            cwd: workingDir,
            instances: 1,
            exec_mode: 'fork',
            autorestart: true,
            watch: false,
            max_memory_restart: '2G',
            env: {
                OMNI_ENV: 'production',
                OMNI_ROOT: ROOT_DIR
            },
            error_file: join(releaseDir, 'omni-err.log'),
            out_file: join(releaseDir, 'omni-out.log'),
            log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
        }]
    };

    const pm2Path = join(releaseDir, 'ecosystem.config.cjs');
    writeFileSync(pm2Path, `module.exports = ${JSON.stringify(pm2Ecosystem, null, 2)};\n`);

    // 4. Output instruksi
    console.log(`✅ [SYSTEMD] File service tercipta: release/${serviceName}.service`);
    console.log(`✅ [SCRIPT]  Auto-installer script: release/install-service.sh`);
    console.log(`✅ [PM2]     Ecosystem fallback   : release/ecosystem.config.cjs`);

    console.log(`\n${'='.repeat(60)}`);
    console.log(`🛡️  OMNI-IMMORTALITY — INSTRUKSI DEPLOYMENT`);
    console.log(`${'='.repeat(60)}`);

    console.log(`\n🔷 OPSI A: Systemd (Rekomendasi — Butuh Root/Sudo)`);
    console.log(`${'─'.repeat(60)}`);
    console.log(`   sudo bash release/install-service.sh`);
    console.log(``);
    console.log(`   Atau manual:`);
    console.log(`   1. sudo cp release/${serviceName}.service /etc/systemd/system/`);
    console.log(`   2. sudo systemctl daemon-reload`);
    console.log(`   3. sudo systemctl enable ${serviceName}`);
    console.log(`   4. sudo systemctl start ${serviceName}`);
    console.log(``);
    console.log(`   Monitoring:`);
    console.log(`   👉 journalctl -u ${serviceName} -f`);

    console.log(`\n🔶 OPSI B: PM2 (Fallback — Tanpa Root)`);
    console.log(`${'─'.repeat(60)}`);
    console.log(`   npm install -g pm2`);
    console.log(`   pm2 start release/ecosystem.config.cjs`);
    console.log(`   pm2 save && pm2 startup`);

    console.log(`\n${'='.repeat(60)}`);
    console.log(`🏆 Status: IMMORTAL. Server Anda menolak untuk mati.`);
    console.log(`${'='.repeat(60)}\n`);
}

// ==========================================
// 📦 OMNI-PKG: DECENTRALIZED MODULE MANAGER
// ==========================================
// Jalur Sutra Digital — Menggunakan GitHub sebagai lautan penyimpanan gratis.
// Developer di seluruh dunia bisa mengunggah modul ke GitHub dan
// developer lain bisa menyedotnya langsung via `omni get <url>`.
//
// Standar Modul OMNI:
//   Setiap repositori modul HARUS berisi:
//   1. omni.module.json  — Kartu Identitas Modul
//   2. worker.go         — Logika Backend (Golang)
//   3. ui.tsx            — Antarmuka React Frontend
//   (Opsional) engine/   — Folder engine C++/Python/JS
// ==========================================

function runOmniGet(githubRepoUrl) {
    if (!githubRepoUrl || !githubRepoUrl.includes('github.com')) {
        console.log("❌ [FATAL] Format URL tidak valid. Gunakan URL GitHub.");
        console.log("💡 Contoh: omni get https://github.com/username/omni-module-name");
        process.exit(1);
    }

    console.log(`\n🛸 [OMNI-PKG] Mengunci target repositori: ${githubRepoUrl}...`);

    // 1. Siapkan Ruang Operasi (Temp Folder)
    const tempDir = join(ROOT_DIR, '.omni_temp_module');
    if (existsSync(tempDir)) rmSync(tempDir, { recursive: true, force: true });

    try {
        // 2. Kloning Repositori secara Senyap (Shallow clone agar super cepat)
        console.log("📥 Mengunduh artefak dari server global...");
        try {
            execSync(`git clone --depth 1 ${githubRepoUrl} "${tempDir}"`, { stdio: 'pipe' });
        } catch (gitErr) {
            throw new Error(`Git clone gagal. Pastikan URL benar dan Anda memiliki akses internet.\n   ${gitErr.stderr ? gitErr.stderr.toString().trim() : gitErr.message}`);
        }

        // 3. Verifikasi Konstitusi (Cek omni.module.json)
        const moduleConfigPath = join(tempDir, 'omni.module.json');
        if (!existsSync(moduleConfigPath)) {
            throw new Error(
                "Bukan Modul OMNI yang sah! File omni.module.json tidak ditemukan.\n" +
                "   Repositori harus mengikuti Standar Modul OMNI.\n" +
                "   Jalankan 'omni make module' untuk membuat template modul."
            );
        }

        const moduleData = JSON.parse(readFileSync(moduleConfigPath, 'utf8'));

        // Validasi field wajib
        if (!moduleData.id || !moduleData.version || !moduleData.author) {
            throw new Error(
                "omni.module.json tidak lengkap! Field wajib: id, version, author."
            );
        }

        const moduleId = moduleData.id;
        console.log(`🔍 [OMNI-PKG] Membedah Modul: \x1b[32m${moduleId}\x1b[0m (v${moduleData.version}) oleh ${moduleData.author}`);
        if (moduleData.description) {
            console.log(`   📋 ${moduleData.description}`);
        }

        // 4. Cek apakah modul sudah terinstal
        const registryPath = join(ROOT_DIR, 'configs', 'cli_registry.json');
        let registry = JSON.parse(readFileSync(registryPath, 'utf8'));

        if (registry.tools[moduleId]) {
            throw new Error(`Modul dengan ID '${moduleId}' sudah terinstal di sistem Anda!\n   Gunakan 'omni remove ${moduleId}' untuk menghapusnya terlebih dahulu.`);
        }

        // 5. Validasi file inti modul
        const goSource = join(tempDir, 'worker.go');
        const tsxSource = join(tempDir, 'ui.tsx');

        if (!existsSync(goSource)) {
            throw new Error("Modul cacat! File worker.go (backend Golang) tidak ditemukan.");
        }
        if (!existsSync(tsxSource)) {
            throw new Error("Modul cacat! File ui.tsx (frontend React) tidak ditemukan.");
        }

        // 6. Transplantasi Organ — Pindahkan file ke jantung OMNI
        const goTargetDir = join(ROOT_DIR, 'api', 'engine');
        const tsxTargetDir = join(ROOT_DIR, 'ui', 'src', 'tools');

        if (!existsSync(goTargetDir)) mkdirSync(goTargetDir, { recursive: true });
        if (!existsSync(tsxTargetDir)) mkdirSync(tsxTargetDir, { recursive: true });

        const goTarget = join(goTargetDir, `worker_${moduleId}.go`);
        const tsxTarget = join(tsxTargetDir, `${moduleId}.tsx`);

        copyFileSync(goSource, goTarget);
        copyFileSync(tsxSource, tsxTarget);

        console.log(`✅ [BACKEND]  Mesin pekerja disuntikkan: api/engine/worker_${moduleId}.go`);
        console.log(`✅ [FRONTEND] Antarmuka disuntikkan   : ui/src/tools/${moduleId}.tsx`);

        // 7. Cek dan salin file engine opsional (C++, Python, C#, JS)
        const engineSource = join(tempDir, 'engine');
        let engineFiles = [];
        if (existsSync(engineSource)) {
            const engineTargetDir = join(ROOT_DIR, 'engine');
            if (!existsSync(engineTargetDir)) mkdirSync(engineTargetDir, { recursive: true });

            const files = readdirSync(engineSource);
            for (const file of files) {
                const srcFile = join(engineSource, file);
                const destFile = join(engineTargetDir, `${moduleId}_${file}`);
                copyFileSync(srcFile, destFile);
                engineFiles.push(file);
            }
            if (engineFiles.length > 0) {
                console.log(`✅ [ENGINE]   Native engines disuntikkan: ${engineFiles.join(', ')}`);
            }
        }

        // 8. Injeksi ke Pusat Komando (cli_registry.json)
        registry.tools[moduleId] = {
            binary: moduleData.binary || 'custom_engine',
            description: moduleData.description || `Community module: ${moduleId}`,
            params: moduleData.params || ['file'],
            source: 'omni-pkg',
            repository: githubRepoUrl,
            version: moduleData.version,
            author: moduleData.author,
            installed_at: new Date().toISOString()
        };

        writeFileSync(registryPath, JSON.stringify(registry, null, 2));
        console.log(`✅ [REGISTRY] Saraf pusat telah diperbarui.`);

        // 9. Sinkronkan Golang Switchboard
        console.log("\n⚙️  [OMNI-PKG] Mengintegrasikan modul ke dalam sistem...");
        try {
            generateGoRegistry();
            console.log(`✅ [GO-SYNC]  Switchboard Golang diperbarui.`);
        } catch (e) {
            console.log(`⚠️  [GO-SYNC]  Auto-sync switchboard gagal (non-fatal): ${e.message}`);
        }

        // 10. Update installed modules manifest
        const manifestPath = join(ROOT_DIR, 'configs', 'omni_modules.json');
        let manifest = existsSync(manifestPath)
            ? JSON.parse(readFileSync(manifestPath, 'utf8'))
            : { modules: {} };

        manifest.modules[moduleId] = {
            version: moduleData.version,
            author: moduleData.author,
            description: moduleData.description || '',
            repository: githubRepoUrl,
            files: {
                backend: `api/engine/worker_${moduleId}.go`,
                frontend: `ui/src/tools/${moduleId}.tsx`,
                engine: engineFiles.map(f => `engine/${moduleId}_${f}`)
            },
            installed_at: new Date().toISOString()
        };

        writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));

        // 11. Laporan Akhir
        console.log(`\n${'='.repeat(60)}`);
        console.log(`🎉 [SUKSES] Modul \x1b[36m${moduleId}\x1b[0m v${moduleData.version} siap digunakan!`);
        console.log(`${'='.repeat(60)}`);
        console.log(`   Oleh     : ${moduleData.author}`);
        console.log(`   Repo     : ${githubRepoUrl}`);
        console.log(`   Backend  : api/engine/worker_${moduleId}.go`);
        console.log(`   Frontend : ui/src/tools/${moduleId}.tsx`);
        if (engineFiles.length > 0) {
            console.log(`   Engine   : ${engineFiles.length} file native`);
        }
        console.log(`${'='.repeat(60)}\n`);

    } catch (error) {
        console.log(`\n❌ [GAGAL] OMNI-PKG membatalkan operasi: ${error.message}`);
        process.exit(1);
    } finally {
        // 12. Protokol Pembersihan (Bakar sisa sampah kloning)
        if (existsSync(tempDir)) rmSync(tempDir, { recursive: true, force: true });
    }
}

// ==========================================
// 🗑️ OMNI-PKG: MODULE REMOVER
// ==========================================
function runOmniRemove(moduleId) {
    if (!moduleId) {
        console.log("❌ Penggunaan: omni remove <module_id>");
        console.log("💡 Gunakan 'omni list modules' untuk melihat modul terinstal.");
        process.exit(1);
    }

    console.log(`\n🗑️  [OMNI-PKG] Menghapus modul: ${moduleId}...`);

    const manifestPath = join(ROOT_DIR, 'configs', 'omni_modules.json');
    if (!existsSync(manifestPath)) {
        console.log("❌ Tidak ada modul komunitas yang terinstal.");
        return;
    }

    const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
    const moduleInfo = manifest.modules[moduleId];

    if (!moduleInfo) {
        console.log(`❌ Modul '${moduleId}' tidak ditemukan di daftar modul komunitas.`);
        console.log("💡 Gunakan 'omni list modules' untuk melihat modul terinstal.");
        return;
    }

    // 1. Hapus file backend
    const goFile = join(ROOT_DIR, moduleInfo.files.backend);
    if (existsSync(goFile)) {
        rmSync(goFile);
        console.log(`✅ Dihapus: ${moduleInfo.files.backend}`);
    }

    // 2. Hapus file frontend
    const tsxFile = join(ROOT_DIR, moduleInfo.files.frontend);
    if (existsSync(tsxFile)) {
        rmSync(tsxFile);
        console.log(`✅ Dihapus: ${moduleInfo.files.frontend}`);
    }

    // 3. Hapus engine files
    if (moduleInfo.files.engine && moduleInfo.files.engine.length > 0) {
        for (const engineFile of moduleInfo.files.engine) {
            const filePath = join(ROOT_DIR, engineFile);
            if (existsSync(filePath)) {
                rmSync(filePath);
                console.log(`✅ Dihapus: ${engineFile}`);
            }
        }
    }

    // 4. Hapus dari cli_registry.json
    const registryPath = join(ROOT_DIR, 'configs', 'cli_registry.json');
    const registry = JSON.parse(readFileSync(registryPath, 'utf8'));
    if (registry.tools[moduleId]) {
        delete registry.tools[moduleId];
        writeFileSync(registryPath, JSON.stringify(registry, null, 2));
        console.log(`✅ Registry diperbarui.`);
    }

    // 5. Hapus dari manifest
    delete manifest.modules[moduleId];
    writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));

    // 6. Re-sync Go switchboard
    try {
        generateGoRegistry();
        console.log(`✅ Switchboard Golang disinkronkan.`);
    } catch (e) {
        console.log(`⚠️  Auto-sync gagal (non-fatal): ${e.message}`);
    }

    console.log(`\n🎉 Modul '${moduleId}' berhasil dihapus dari sistem.\n`);
}

// ==========================================
// 📋 OMNI-PKG: LIST COMMUNITY MODULES
// ==========================================
function listOmniModules() {
    const manifestPath = join(ROOT_DIR, 'configs', 'omni_modules.json');
    if (!existsSync(manifestPath)) {
        console.log("\n📋 [OMNI-PKG] Tidak ada modul komunitas yang terinstal.");
        console.log("💡 Gunakan 'omni get <github-url>' untuk menginstal modul.\n");
        return;
    }

    const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
    const modules = Object.entries(manifest.modules);

    if (modules.length === 0) {
        console.log("\n📋 [OMNI-PKG] Tidak ada modul komunitas yang terinstal.");
        console.log("💡 Gunakan 'omni get <github-url>' untuk menginstal modul.\n");
        return;
    }

    console.log(`\n${'='.repeat(60)}`);
    console.log(`📦 OMNI-PKG: Modul Komunitas Terinstal (${modules.length})`);
    console.log(`${'='.repeat(60)}`);

    for (const [id, info] of modules) {
        console.log(`\n   ▸ \x1b[36m${id}\x1b[0m v${info.version}`);
        console.log(`     Oleh    : ${info.author}`);
        if (info.description) console.log(`     Desc    : ${info.description}`);
        console.log(`     Repo    : ${info.repository}`);
        console.log(`     Instal  : ${info.installed_at}`);
    }

    console.log(`\n${'='.repeat(60)}`);
    console.log(`💡 Hapus modul: omni remove <module_id>`);
    console.log(`${'='.repeat(60)}\n`);
}

// ==========================================
// 📐 OMNI-PKG: MODULE TEMPLATE GENERATOR
// ==========================================
function generateModuleTemplate(moduleName) {
    if (!moduleName) {
        console.log("❌ Penggunaan: omni make module <nama_modul>");
        console.log("💡 Contoh: omni make module pdf_compressor");
        return;
    }

    const moduleDir = join(process.cwd(), `omni-${moduleName}`);
    if (existsSync(moduleDir)) {
        console.log(`❌ Folder 'omni-${moduleName}' sudah ada!`);
        return;
    }

    console.log(`\n📐 [OMNI-PKG] Membuat template modul: omni-${moduleName}...`);

    mkdirSync(moduleDir, { recursive: true });
    mkdirSync(join(moduleDir, 'engine'), { recursive: true });

    // 1. omni.module.json
    const moduleJson = {
        id: moduleName,
        version: "1.0.0",
        author: "Your Name",
        description: `OMNI Module: ${moduleName.replace(/_/g, ' ')}`,
        binary: "custom_engine",
        params: ["file"]
    };
    writeFileSync(join(moduleDir, 'omni.module.json'), JSON.stringify(moduleJson, null, 2));

    // 2. worker.go
    const goTemplate = `package engine

import (
\t"fmt"
\t"net/http"
)

// ${moduleName} — OMNI Community Module
// Handler untuk tool: ${moduleName}
func Handle_${moduleName}(w http.ResponseWriter, r *http.Request) {
\tfmt.Fprintf(w, `+"`"+`{"status": "OK", "tool": "${moduleName}", "message": "Module is working!"}`+"`"+`)
}
`;
    writeFileSync(join(moduleDir, 'worker.go'), goTemplate);

    // 3. ui.tsx
    const tsxTemplate = `'use client';
import React, { useState } from 'react';

/**
 * ${moduleName} — OMNI Community Module UI
 * Antarmuka React untuk tool: ${moduleName}
 */
export default function ${moduleName.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('')}Tool() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState('idle');

  const handleProcess = async () => {
    if (!file) return;
    setStatus('processing');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/v1/process?tool_id=${moduleName}', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setStatus(data.status === 'OK' ? 'success' : 'error');
    } catch (err) {
      setStatus('error');
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>${moduleName.replace(/_/g, ' ').toUpperCase()}</h2>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <button onClick={handleProcess} disabled={!file || status === 'processing'}>
        {status === 'processing' ? 'Processing...' : 'Process'}
      </button>
      <p>Status: {status}</p>
    </div>
  );
}
`;
    writeFileSync(join(moduleDir, 'ui.tsx'), tsxTemplate);

    // 4. README.md
    const readme = `# omni-${moduleName}

OMNI Community Module: **${moduleName.replace(/_/g, ' ')}**

## Installation

\`\`\`bash
omni get https://github.com/YOUR_USERNAME/omni-${moduleName}
\`\`\`

## Structure

\`\`\`
omni-${moduleName}/
├── omni.module.json    # Module manifest (REQUIRED)
├── worker.go           # Backend handler (REQUIRED)
├── ui.tsx              # Frontend component (REQUIRED)
├── engine/             # Native engines (OPTIONAL)
│   ├── processor.py    # Python engine
│   ├── processor.cpp   # C++ engine
│   └── processor.js    # JavaScript engine
└── README.md
\`\`\`

## OMNI Module Standard

All OMNI community modules must contain:
1. \`omni.module.json\` — Module identity card
2. \`worker.go\` — Backend logic (Golang)
3. \`ui.tsx\` — Frontend React component

## License

MIT
`;
    writeFileSync(join(moduleDir, 'README.md'), readme);

    // 5. .gitignore
    writeFileSync(join(moduleDir, '.gitignore'), 'node_modules/\n.omni_temp_module/\n');

    console.log(`✅ Template modul dibuat di: omni-${moduleName}/`);
    console.log(``);
    console.log(`📁 Struktur:`);
    console.log(`   omni-${moduleName}/`);
    console.log(`   ├── omni.module.json   ← Kartu identitas modul`);
    console.log(`   ├── worker.go          ← Backend Golang`);
    console.log(`   ├── ui.tsx             ← Frontend React`);
    console.log(`   ├── engine/            ← Native engines (opsional)`);
    console.log(`   ├── README.md          ← Dokumentasi`);
    console.log(`   └── .gitignore`);
    console.log(``);
    console.log(`🚀 Langkah selanjutnya:`);
    console.log(`   1. Edit worker.go dan ui.tsx sesuai kebutuhan`);
    console.log(`   2. git init && git add . && git commit -m "Initial"`);
    console.log(`   3. Push ke GitHub`);
    console.log(`   4. Developer lain bisa install: omni get <github-url>`);
    console.log(``);
}

// ==========================================
// ⚔️ OMNI-TEST: THE SELF-TORTURE ENGINE
// ==========================================
async function runOmniTest() {
    console.log("\n⚔️ [OMNI-TEST] Memlaporkan Protokol Simulasi Serangan...");
    
    const registry = JSON.parse(readFileSync(join(ROOT_DIR, 'configs', 'cli_registry.json'), 'utf8'));
    let tools = Object.keys(registry.tools).filter(id => !id.startsWith('=') && !id.startsWith('_CATEGORY'));
    
    // Support filtering by tool ID if provided in argv
    const filterArg = process.argv.find(arg => arg.startsWith('--tool='));
    if (filterArg) {
        const targetTool = filterArg.split('=')[1];
        tools = tools.filter(id => id === targetTool);
    }

    let passed = 0;
    let failed = 0;

    for (const toolId of tools) {
        process.stdout.write(`🧪 Menguji Modul [${toolId}]... `);
        
        // Simulasi Request Multipart/Form-Data mentah
        const success = await simulateRequest(toolId);
        
        if (success) {
            console.log("\x1b[32mPASSED\x1b[0m");
            passed++;
        } else {
            console.log("\x1b[31mFAILED\x1b[0m");
            failed++;
        }
    }

    console.log(`\n📊 [HASIL UJI] Total: ${tools.length} | ✅ Lolos: ${passed} | ❌ Gagal: ${failed}`);
    if (failed > 0) {
        console.log("⚠️ [WARNING] Sistem tidak stabil. Periksa Log sebelum rilis!");
        process.exit(1);
    }
}


// Fungsi bantuan untuk mengecek status (Polling) dihapus, karena REST API ini synchronous (menunggu selesai)


// Mesin Simulasi Sempurna (Deep Validation)
async function simulateRequest(toolId) {
    return new Promise((resolve) => {
        const boundary = '----OmniTestBoundary' + Date.now();
        
        // Kita gunakan file biner kosong agar FFmpeg/Worker tidak crash dengan file .txt
        // NOTE: Harus pakai nama 'omni_file' agar diterima FileQuarantineHandler
        const postData = 
            `--${boundary}\r\n` +
            `Content-Disposition: form-data; name="omni_file"; filename="test_dummy.bin"\r\n` +
            `Content-Type: application/octet-stream\r\n\r\n` +
            `\x00\x00\x00\x00\x00\x00\x00\x00\r\n` +
            `--${boundary}--\r\n`;

        const options = {
            hostname: 'localhost',
            port: 3000,
            path: `/api/v1/omni/execute?tool_id=${toolId}`,
            method: 'POST',
            headers: { 
                'X-OMNI-INTERNAL-TEST': 'OMNI_GOD_MODE_999', // ⚡ Lewati blokade Middleware
                'Content-Type': `multipart/form-data; boundary=${boundary}`,
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            
            res.on('end', async () => {
                if (res.statusCode !== 202 && res.statusCode !== 200) {
                    // Coba baca pesan error dari golang
                    let errorMsg = `Status HTTP ${res.statusCode}`;
                    try {
                        const jsonErr = JSON.parse(data);
                        if (jsonErr.message) errorMsg = jsonErr.message;
                    } catch (e) {}
                    console.log(`\n   ❌ [Ditolak Server] ${errorMsg}`);
                    return resolve(false);
                }

                try {
                    const jsonRes = JSON.parse(data);
                    if (jsonRes.success === true) {
                        return resolve(true);
                    } else {
                        console.log(`\n   ❌ [Gagal Eksekusi] ${jsonRes.message || 'Unknown Error'}`);
                        return resolve(false);
                    }
                } catch (e) {
                    console.log(`\n   ❌ [Crash JSON] Output Golang tidak valid: ` + data.substring(0, 50));
                    resolve(false);
                }
            });
        });

        req.on('error', (err) => {
            console.log(`\n   ❌ [Koneksi Gagal] Golang Gateway Mati! (${err.message})`);
            resolve(false);
        });
        req.write(postData);
        req.end();
    });
}

async function runStressTest() {
    console.log("🔥 [STRESS-TEST] Menembakkan 100 Request Serentak...");
    const startTime = Date.now();
    
    const attacks = Array.from({ length: 100 }).map(() => simulateRequest('demo_tool'));
    const results = await Promise.all(attacks);
    
    const successCount = results.filter(r => r).length;
    const duration = (Date.now() - startTime) / 1000;
    
    console.log(`🚀 Selesai dalam ${duration} detik. Sukses: ${successCount}/100`);
    if (successCount < 100) console.log("⚠️ Terjadi packet loss dalam antrean internal!");
}

switch (command) {
    case 'test':
        console.log("🔍 Memastikan OMNI Gateway aktif...");
        await runOmniTest();
        await runStressTest();
        break;
    case 'init':
        initProject(projectName);
        break;
    case 'parse':
        runOmniParse();
        break;
    case 'sphere':
        runOmniSphere();
        break;
    case 'dev':
        // Jalankan diagnostik massal DULU sebelum menyalakan server!
        console.log("🔍 Menjalankan Pre-Flight Diagnostic...");
        runDeepDiagnostics(); 
        
        startDevServer();
        break;
    case 'scan':
        runDeepDiagnostics();
        break;
    case 'build':
        enforceRoleIsolation();
        generateGoRegistry(); // Sinkronkan sebelum build
        runBuildProcess();
        break;
    case 'install':
        if (args[1] === 'bin' || args[1] === 'tools') {
            const missing = await getMissingDependencies();
            if (missing.length > 0) {
                await runAutoInstall(missing);
            } else {
                console.log("✅ Semua binari (FFmpeg, Pandoc, dll) sudah terpasang.");
            }
        } else if (args.length > 1) {
            installSpecificPackage(args[1], args[2]);
        } else {
            installAllFromManifest();
        }
        break;
    case 'add-tool':
        addUniversalTool();
        break;
    case 'make':
        const makeType = args[1];
        if (makeType === 'docs') {
            generateOmniDocs(); // Ekstrak JSON
            // Copy file HTML viewer ke release
            try {
                copyFileSync(join(ROOT_DIR, 'ui', 'docs.html'), join(ROOT_DIR, 'release', 'public', 'docs.html'));
            } catch (_) { /* docs.html opsional */ }
            console.log("🚀 [OMNI-DOCS] Dokumentasi API siap diakses di http://localhost:3000/docs.html");
        } else if (makeType === 'service') {
            generateSystemdService(); // 🛡️ OMNI-IMMORTALITY: Kernel Service Generator
        } else if (makeType === 'module') {
            generateModuleTemplate(args[2]); // 📐 OMNI-PKG: Module Template Generator
        } else if (makeType === 'tool') {
            runOmniForge(args[2]);
            generateGoRegistry(); // Sinkronkan setelah buat tool baru
        } else {
            console.log("❌ Penggunaan:");
            console.log("   omni make tool <nama_fitur>   — Buat tool baru");
            console.log("   omni make docs                — Generate API docs");
            console.log("   omni make service             — Generate Systemd service (Linux Production)");
            console.log("   omni make module <nama_modul> — Generate template modul komunitas");
        }
        break;
    case 'fix':
        await runOmniDoctor();
        break;
    case 'upgrade-logic':
        evolveCodebase();
        break;
    case 'theme':
        changeTheme(args[1]);
        break;
    case 'sync':
        generateGoRegistry();
        break;

    // 📦 OMNI-PKG: Decentralized Module Manager
    case 'get':
        runOmniGet(args[1]);
        break;
    case 'remove':
        runOmniRemove(args[1]);
        break;
    case 'list':
        if (args[1] === 'modules') {
            listOmniModules();
        } else {
            console.log("💡 Penggunaan: omni list modules");
        }
        break;

    // 👻 OMNI DAEMON: PRODUCTION PROCESS MANAGER
    case 'start':
        runOmniDaemon();
        break;
    case 'stop':
        stopOmniDaemon();
        break;
    case 'status':
        statusOmniDaemon();
        break;
    case 'restart':
        console.log("🔄 [OMNI DAEMON] Restart Protocol...");
        stopOmniDaemon();
        // Tunggu sebentar agar port dibebaskan
        await new Promise(r => setTimeout(r, 1500));
        runOmniDaemon();
        break;
    case 'logs':
        console.log("\n📋 [OMNI DAEMON] Log Aktivitas Terakhir:\n");
        const logPath = join(ROOT_DIR, 'release', 'omni-out.log');
        const errLogPath = join(ROOT_DIR, 'release', 'omni-err.log');
        if (existsSync(logPath)) {
            const content = readFileSync(logPath, 'utf8');
            const lines = content.split('\n').slice(-50).join('\n');
            console.log(lines);
        } else {
            console.log("⚠️  File log belum ada. Jalankan 'omni start' terlebih dahulu.");
        }
        if (existsSync(errLogPath)) {
            const errContent = readFileSync(errLogPath, 'utf8').trim();
            if (errContent) {
                console.log("\n🔴 Error Log:");
                console.log(errContent.split('\n').slice(-20).join('\n'));
            }
        }
        console.log();
        break;

    default:
        console.log("❌ Perintah tidak dikenali. Gunakan:\n");
        console.log("   📦 DEVELOPMENT");
        console.log("   omni init [nama-proyek]       -> 🌐 Bootstrap proyek dari Omnifile");
        console.log("   omni dev                      -> 📡 OMNI-RESONANCE Dev Server");
        console.log("   omni scan                     -> 👁️ The Eye of Omni: Deep Diagnostics");
        console.log("   omni fix                      -> 🩺 OmniDoctor: Perbaikan Otomatis");
        console.log();
        console.log("   🏭 BUILD & DEPLOY");
        console.log("   omni build                    -> Membangun rilis produksi");
        console.log("   omni sphere                   -> 🌐 OMNI-SPHERE: Build biner mandiri (SEA)");
        console.log("   omni start                    -> 👻 Nyalakan Daemon Produksi (background)");
        console.log("   omni stop                     -> 🛑 Matikan Daemon Produksi");
        console.log("   omni restart                  -> 🔄 Restart Daemon Produksi");
        console.log("   omni status                   -> 📡 Cek status Daemon");
        console.log("   omni logs                     -> 📋 Lihat log Daemon");
        console.log();
        console.log("   📜 OMNIFILE");
        console.log("   omni parse                    -> 📜 Parse & tampilkan isi Omnifile");
        console.log();
        console.log("   🔧 TOOLS & CONFIG");
        console.log("   omni install bin              -> Instal binari sistem (FFmpeg, Pandoc, Magick)");
        console.log("   omni install ui <paket>       -> Instal paket JSX/TypeScript (npm)");
        console.log("   omni install api <paket>      -> Instal paket Golang (go get)");
        console.log("   omni install ai <paket>       -> Instal paket Python (pip)");
        console.log("   omni install engine <paket>   -> Instal library C++ (vcpkg)");
        console.log("   omni add-tool --id <id> ...   -> Menambahkan tool ke JSON & React");
        console.log("   omni make tool <id>           -> 🔨 OMNI-FORGE: Scaffold Go & React instan");
        console.log("   omni make docs                -> 📖 OMNI-DOCS: Update autogenerator dokumentasi mandiri");
        console.log("   omni make service             -> 🛡️ OMNI-IMMORTALITY: Generate Systemd service");
        console.log("   omni make module <nama>       -> 📐 Generate template modul komunitas");
        console.log("   omni upgrade-logic            -> 🧬 OMNI-SYNTHESIZER: Sync Registry -> UI");
        console.log("   omni theme <framework>        -> 🦎 OMNI-CHAMELEON: Ganti tema CSS");
        console.log("   omni test                     -> ⚔️ OMNI-TEST: Jalankan simulasi serangan & stress test");
        console.log();
        console.log("   📦 OMNI-PKG: Decentralized Module Manager");
        console.log("   omni get <github-url>         -> 🛸 Unduh & instal modul komunitas dari GitHub");
        console.log("   omni remove <module_id>       -> 🗑️  Hapus modul komunitas");
        console.log("   omni list modules             -> 📋 Lihat modul komunitas terinstal\n");
        process.exit(1);
}

// ==========================================
// LOGIKA 1: omni init (Scaffolding via Omnifile)
// ==========================================
function initProject(name) {
    console.log("\n" + "=".repeat(60));
    console.log("🌐 OMNI-SPHERE: PROJECT BOOTSTRAP ENGINE");
    console.log("=".repeat(60) + "\n");

    // ===== DETEKSI OMNIFILE =====
    const omnifilePath = locateOmnifile(ROOT_DIR);
    let omniConfig = null;

    if (omnifilePath) {
        console.log(`📜 [OMNIFILE] Ditemukan: ${omnifilePath}`);
        try {
            omniConfig = parseOmnifile(omnifilePath);
            prettyPrintConfig(omniConfig);
        } catch (err) {
            console.error(`❌ [FATAL] Gagal membaca Omnifile: ${err.message}`);
            process.exit(1);
        }
    } else {
        console.log("📜 [OMNIFILE] Tidak ditemukan. Menggunakan konfigurasi default.");
        omniConfig = {
            APP_NAME: name || 'omni-project',
            VERSION: '1.0.0',
            PORT: 3000,
            THEME: 'tailwind',
            REQUIRE_TOOLS: ['demo_tool'],
            ENVIRONMENT: 'development',
            PERSISTENCE: false,
            MAX_UPLOAD_GB: 50,
        };
    }

    // ===== TENTUKAN TARGET DIR =====
    const projectName = omniConfig.APP_NAME
        ? omniConfig.APP_NAME.replace(/\s+/g, '-').toLowerCase()
        : name || 'omni-project';
    const targetDir = join(ROOT_DIR, projectName);

    if (existsSync(targetDir)) {
        console.log(`⚠️  Folder '${projectName}' sudah ada. Melanjutkan ke dalam folder...`);
    } else {
        mkdirSync(targetDir, { recursive: true });
    }

    console.log(`\n📦 [STEP 1/6] Membangun arsitektur folder...`);

    // ===== STRUKTUR FOLDER =====
    const folders = [
        'api/middleware', 'api/routes', 'api/services', 'api/engine', 'api/core',
        'engine/audio_tools', 'engine/video_tools',
        'ui/src/components', 'ui/src/pages', 'ui/src/configs', 'ui/src/modules',
        'scripts/ai_tools', 'scripts/build_tools',
        'configs', 'logs', 'lib',
        'release/omni_quarantine', 'release/omni_cache', 'release/bin', 'release/public'
    ];
    folders.forEach(f => mkdirSync(join(targetDir, f), { recursive: true }));
    console.log(`   ✅ ${folders.length} direktori diciptakan.`);

    // ===== STEP 2: GENERATE APPCONFIG.JSON =====
    console.log(`\n⚙️  [STEP 2/6] Membangkitkan appconfig.json dari Omnifile...`);
    const appConfig = toAppConfig(omniConfig);
    writeFileSync(
        join(targetDir, 'configs', 'appconfig.json'),
        JSON.stringify(appConfig, null, 2)
    );
    console.log(`   ✅ configs/appconfig.json berhasil di-generate.`);

    // ===== STEP 3: GENERATE .ENV =====
    console.log(`\n🔐 [STEP 3/6] Membangkitkan .env dari blok ENV...`);
    let envContent = '# OMNI TOOLS - Auto-Generated Environment Variables\n';
    envContent += `OMNI_ENV=${omniConfig.ENVIRONMENT || 'development'}\n`;
    if (omniConfig.ENV && typeof omniConfig.ENV === 'object') {
        for (const [k, v] of Object.entries(omniConfig.ENV)) {
            envContent += `${k}=${v}\n`;
        }
    }
    writeFileSync(join(targetDir, '.env'), envContent);
    console.log(`   ✅ .env berhasil di-generate.`);

    // ===== STEP 4: GENERATE OMNI.JSON =====
    console.log(`\n📋 [STEP 4/6] Membangkitkan omni.json manifest...`);
    const omniJson = {
        framework: 'OMNI TOOLS',
        appName: omniConfig.APP_NAME || projectName,
        version: omniConfig.VERSION || '1.0.0',
        ephemeralMode: true,
        cacheTTLMinutes: 60,
        network: {
            gatewayPort: omniConfig.PORT || 3000,
            allowedOrigins: ['*']
        },
        universalDependencies: {
            ui_jsx: [],
            api_golang: [],
            ai_python: [],
            engine_cpp: []
        },
        security: {
            requireAuth: true,
            maxPayloadSizeMB: (omniConfig.MAX_UPLOAD_GB || 50) * 1024,
            universalErrorFormat: true
        }
    };
    writeFileSync(join(targetDir, 'omni.json'), JSON.stringify(omniJson, null, 2));
    console.log(`   ✅ omni.json berhasil di-generate.`);

    // ===== STEP 5: GITIGNORE =====
    writeFileSync(join(targetDir, '.gitignore'), [
        'node_modules/', '.env', 'release/omni_cache/', 'release/omni_quarantine/',
        'logs/', '__pycache__/', '*.exe', '*.o', '*.so', '.venv/', '.omni_temp_module/'
    ].join('\n'));

    // ===== STEP 5: OMNI-FORGE — Generate semua tool dari REQUIRE_TOOLS =====
    console.log(`\n🔨 [STEP 5/6] OMNI-FORGE: Menempa ${(omniConfig.REQUIRE_TOOLS || []).length} senjata dari Omnifile...`);
    const requiredTools = omniConfig.REQUIRE_TOOLS || [];

    if (requiredTools.length > 0) {
        // Buat CLI registry base
        const cliRegistry = { tools: {} };
        const registryOmni = { tools: [] };

        for (const toolId of requiredTools) {
            console.log(`   🔧 Menempa: ${toolId}`);

            // Registry entry
            cliRegistry.tools[toolId] = {
                binary: 'auto_generated',
                input_ext: '',
                output_ext: '',
                description: `Auto-scaffolded from Omnifile: ${toolId}`
            };

            // Metadata entry
            const prettyName = toolId.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
            let category = 'SYSTEM';
            if (toolId.startsWith('video_')) category = 'VIDEO';
            else if (toolId.startsWith('audio_')) category = 'AUDIO';
            else if (toolId.startsWith('pdf_')) category = 'PDF';
            else if (toolId.startsWith('conv_') || toolId.startsWith('converter_')) category = 'CONVERTER';
            else if (toolId.startsWith('ai_') || toolId.startsWith('llm_')) category = 'LLM';
            else if (toolId.startsWith('kinetic_')) category = 'SYSTEM';

            registryOmni.tools.push({
                id: toolId,
                category,
                name: prettyName,
                description: `Generated from Omnifile`,
                endpoint: '/api/v1/tools/universal/execute',
                accepts: '*/*',
                delegateTo: toolId.startsWith('kinetic_') ? 'C' : 'C++',
                extraInputs: []
            });
        }

        writeFileSync(join(targetDir, 'configs', 'cli_registry.json'), JSON.stringify(cliRegistry, null, 2));
        writeFileSync(join(targetDir, 'configs', 'registry_omni.json'), JSON.stringify(registryOmni, null, 2));
        console.log(`   ✅ ${requiredTools.length} alat terdaftar di registry.`);
    } else {
        console.log(`   ⚠️ Tidak ada REQUIRE_TOOLS di Omnifile. Registry kosong.`);
    }

    // ===== STEP 6: Salin Omnifile ke dalam proyek =====
    console.log(`\n📜 [STEP 6/6] Menyalin Omnifile ke root proyek...`);
    if (omnifilePath && omnifilePath !== join(targetDir, 'Omnifile')) {
        copyFileSync(omnifilePath, join(targetDir, 'Omnifile'));
    } else if (!existsSync(join(targetDir, 'Omnifile'))) {
        // Generate default Omnifile
        writeFileSync(join(targetDir, 'Omnifile'), generateOmnifileContent(omniConfig));
    }
    console.log(`   ✅ Omnifile berhasil ditanamkan.`);

    // ===== LAPORAN AKHIR =====
    console.log("\n" + "=".repeat(60));
    console.log("🎉 OMNI-SPHERE: BOOTSTRAP SELESAI!");
    console.log("=".repeat(60));
    console.log(`   📛 Proyek  : ${omniConfig.APP_NAME || projectName}`);
    console.log(`   📁 Lokasi  : ${targetDir}`);
    console.log(`   🚪 Port    : ${omniConfig.PORT || 3000}`);
    console.log(`   🔨 Tools   : ${requiredTools.length} alat di-scaffold`);
    console.log(`   📜 Sumber  : ${omnifilePath ? 'Omnifile' : 'Default config'}`);
    console.log("=".repeat(60));
    console.log(`\n➡️  Langkah berikutnya:`);
    console.log(`   cd ${projectName}`);
    console.log(`   omni install`);
    console.log(`   omni dev\n`);
}

// ==========================================
// 📜 OMNI PARSE: DRY-RUN OMNIFILE PARSER
// ==========================================
function runOmniParse() {
    console.log("\n📜 [OMNI PARSE] Membaca Omnifile di direktori ini...\n");

    const omnifilePath = locateOmnifile(ROOT_DIR);
    if (!omnifilePath) {
        console.log("❌ [FATAL] Omnifile tidak ditemukan!");
        console.log("💡 Buat file bernama 'Omnifile' (tanpa ekstensi) di root proyek.");
        console.log("📎 Gunakan 'Omnifile.example' sebagai template.\n");
        process.exit(1);
    }

    console.log(`📍 Lokasi: ${omnifilePath}`);
    const config = parseOmnifile(omnifilePath);
    prettyPrintConfig(config);

    // Convert dan tampilkan appconfig.json preview
    const appConfig = toAppConfig(config);
    console.log("🔄 [PREVIEW] appconfig.json yang akan dihasilkan:");
    console.log(JSON.stringify(appConfig, null, 2));
    console.log();
}

// ==========================================
// 🌐 OMNI SPHERE: SEA BINARY BUILDER
// ==========================================
function runOmniSphere() {
    console.log("\n" + "=".repeat(60));
    console.log("🌐 OMNI-SPHERE: SINGLE EXECUTABLE APPLICATION (SEA) BUILD");
    console.log("=".repeat(60) + "\n");

    const buildScript = join(ROOT_DIR, 'scripts', 'build_sea.mjs');
    if (!existsSync(buildScript)) {
        console.error("❌ [FATAL] scripts/build_sea.mjs tidak ditemukan!");
        console.log("💡 Pastikan file SEA builder tersedia di folder scripts/.");
        process.exit(1);
    }

    try {
        execSync(`node "${buildScript}"`, { cwd: ROOT_DIR, stdio: 'inherit' });
    } catch (err) {
        console.error("\n❌ SEA Build gagal. Periksa error di atas.");
        process.exit(1);
    }
}

// ==========================================
// LOGIKA 3: omni build (OMNI-COMPILER PIPELINE)
// ==========================================
function runBuildProcess() {
    const buildStart = Date.now();
    
    console.log("\n==========================================");
    console.log("🏭 OMNI BUILD PIPELINE — FULL PRODUCTION");
    console.log("==========================================");
    console.log("   Build System : OMNI-COMPILER (esbuild bare-metal)");
    console.log("   Vite Status  : ☠️  ERADICATED");
    console.log("==========================================\n");
    
    // 1. SYNC FIRST: Pastikan semua 152 tools tersinkronisasi ke React
    console.log("🧬 [STEP 1/3] Menjalankan OMNI-Synthesizer (Registry Sync)...");
    evolveCodebase();

    // 2. BUILD FRONTEND (OMNI NATIVE COMPILER)
    console.log("\n🏭 [STEP 2/3] OMNI-COMPILER: Mengkompilasi Frontend...");
    const releasePublicDir = join(ROOT_DIR, 'release', 'public');
    if (!existsSync(releasePublicDir)) mkdirSync(releasePublicDir, { recursive: true });

    try {
        execSync(`node scripts/omni_compiler.mjs`, { cwd: join(ROOT_DIR, 'ui'), stdio: 'inherit' });
    } catch (err) {
        console.error("❌ [OMNI-COMPILER FATAL] Gagal mengkompilasi Frontend.");
        process.exit(1);
    }

    // 3. BUILD BACKEND (GOLANG GATEWAY)
    console.log("\n🐹 [STEP 3/3] Mengkompilasi Golang API Gateway...");
    const releaseBinDir = join(ROOT_DIR, 'release', 'bin');
    if (!existsSync(releaseBinDir)) mkdirSync(releaseBinDir, { recursive: true });
    
    const binaryExt = os.platform() === 'win32' ? '.exe' : '';
    const binaryName = `omni-gateway${binaryExt}`;
    
    try {
        execSync(`go build -o ../release/bin/${binaryName} main.go`, { cwd: join(ROOT_DIR, 'api'), stdio: 'inherit' });
    } catch (err) {
        console.error("❌ Gagal mengkompilasi Golang Gateway.");
        process.exit(1);
    }

    const totalElapsed = ((Date.now() - buildStart) / 1000).toFixed(2);
    
    console.log("\n==========================================");
    console.log("✅ OMNI BUILD PIPELINE — COMPLETE");
    console.log("==========================================");
    console.log(`⏱️  Total waktu build : ${totalElapsed} detik`);
    console.log(`📁  Frontend output   : release/public/`);
    console.log(`📁  Backend binary    : release/bin/${binaryName}`);
    console.log(`🏭  Compiler          : OMNI-COMPILER v1.0 (esbuild)`);
    console.log("==========================================");
    console.log(`\n➡️  Jalankan produksi: cd release/bin && ./${binaryName}`);
}

// ==========================================
// LOGIKA 4: OPM - INSTALASI PAKET SPESIFIK
// ==========================================
function installSpecificPackage(layer, packageName) {
    if (!packageName) {
        console.error("❌ Nama paket tidak boleh kosong! Contoh: omni install ui react");
        process.exit(1);
    }

    console.log(`\n📦 OPM mengunduh [${packageName}] untuk layer [${layer.toUpperCase()}]...\n`);

    try {
        switch (layer) {
                case 'ui':
                // Dunia JavaScript/TypeScript (NPM)
                execSync(`npm install ${packageName}`, { cwd: join(ROOT_DIR, 'ui'), stdio: 'inherit' });
                break;
            case 'api':
                // Dunia Golang (Go Modules)
                execSync(`go get ${packageName}`, { cwd: join(ROOT_DIR, 'api'), stdio: 'inherit' });
                break;
            case 'ai':
                // Dunia Python (PIP)
                execSync(`pip install ${packageName}`, { cwd: join(ROOT_DIR, 'scripts', 'ai_tools'), stdio: 'inherit' });
                // Bekukan dependencies Python ke requirements.txt
                try {
                    execSync(`pip freeze > requirements.txt`, { cwd: join(ROOT_DIR, 'scripts', 'ai_tools') });
                    console.log("📋 requirements.txt diperbarui.");
                } catch (_) { /* Abaikan jika freeze gagal */ }
                break;
            case 'engine':
                // Dunia C++ (VCPKG — Standar Industri)
                console.log("⚙️  Menggunakan VCPKG untuk C++ Library...");
                execSync(`vcpkg install ${packageName}`, { cwd: join(ROOT_DIR, 'engine'), stdio: 'inherit' });
                break;
            default:
                console.error("❌ Layer tidak valid. Gunakan: ui, api, ai, atau engine.");
                console.log("   Contoh: omni install ui axios");
                console.log("   Contoh: omni install api github.com/gorilla/mux");
                console.log("   Contoh: omni install ai transformers");
                console.log("   Contoh: omni install engine opencv4");
                process.exit(1);
        }
        console.log(`\n✅ Paket [${packageName}] berhasil diintegrasikan ke layer [${layer.toUpperCase()}] OMNI TOOLS!`);
    } catch (error) {
        console.error(`\n❌ Gagal menginstal [${packageName}]. Pastikan koneksi internet stabil dan tool CLI layer tersebut terinstal.`);
    }
}

// ==========================================
// LOGIKA 5: OPM - INSTALASI MASSAL DARI omni.json
// ==========================================
function installAllFromManifest() {
    console.log("🌍 OMNI PACKAGE MANAGER (OPM): Membaca manifest universal...\n");

    // Cari omni.json
    const manifestPath = join(ROOT_DIR, 'omni.json');
    if (!existsSync(manifestPath)) {
        console.error("❌ File omni.json tidak ditemukan! Jalankan 'omni init' terlebih dahulu.");
        process.exit(1);
    }

    const omniConfig = JSON.parse(readFileSync(manifestPath, 'utf8'));
    const deps = omniConfig.universalDependencies;

    if (!deps) {
        console.log("ℹ️  Tidak ada blok 'universalDependencies' di omni.json. Tidak ada yang diinstal.");
        return;
    }

    let totalInstalled = 0;

    // === LAYER 1: UI (TypeScript/JSX via NPM) ===
    if (deps.ui_jsx && deps.ui_jsx.length > 0) {
        console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        console.log(`🎨 [LAYER UI] Menginstal ${deps.ui_jsx.length} paket JSX/TypeScript...`);
        console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        try {
            execSync(`npm install ${deps.ui_jsx.join(' ')}`, { cwd: join(ROOT_DIR, 'ui'), stdio: 'inherit' });
            totalInstalled += deps.ui_jsx.length;
            console.log("✅ Layer UI selesai.\n");
        } catch (e) {
            console.error("⚠️  Beberapa paket UI gagal diinstal. Lanjut ke layer berikutnya...\n");
        }
    }

    // === LAYER 2: API (Golang via Go Modules) ===
    if (deps.api_golang && deps.api_golang.length > 0) {
        console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        console.log(`🐹 [LAYER API] Menginstal ${deps.api_golang.length} paket Golang...`);
        console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        try {
            execSync(`go get ${deps.api_golang.join(' ')}`, { cwd: join(ROOT_DIR, 'api'), stdio: 'inherit' });
            totalInstalled += deps.api_golang.length;
            console.log("✅ Layer API selesai.\n");
        } catch (e) {
            console.error("⚠️  Beberapa paket Golang gagal diinstal. Lanjut ke layer berikutnya...\n");
        }
    }

    // === LAYER 3: AI (Python via PIP) ===
    if (deps.ai_python && deps.ai_python.length > 0) {
        console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        console.log(`🐍 [LAYER AI] Menginstal ${deps.ai_python.length} paket Python...`);
        console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        try {
            execSync(`pip install ${deps.ai_python.join(' ')}`, { cwd: join(ROOT_DIR, 'scripts', 'ai_tools'), stdio: 'inherit' });
            totalInstalled += deps.ai_python.length;
            console.log("✅ Layer AI selesai.\n");
        } catch (e) {
            console.error("⚠️  Beberapa paket Python gagal diinstal. Lanjut ke layer berikutnya...\n");
        }
    }

    // === LAYER 4: ENGINE (C++ via VCPKG) ===
    if (deps.engine_cpp && deps.engine_cpp.length > 0) {
        console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        console.log(`🔧 [LAYER ENGINE] Menginstal ${deps.engine_cpp.length} library C++...`);
        console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        try {
            execSync(`vcpkg install ${deps.engine_cpp.join(' ')}`, { cwd: join(ROOT_DIR, 'engine'), stdio: 'inherit' });
            totalInstalled += deps.engine_cpp.length;
            console.log("✅ Layer Engine selesai.\n");
        } catch (e) {
            console.error("⚠️  VCPKG tidak terdeteksi atau library C++ gagal diinstal.\n");
        }
    }

    console.log("=========================================");
    console.log(`🌍 OPM SELESAI: ${totalInstalled} paket lintas ${Object.keys(deps).length} bahasa terinstal.`);
    console.log("=========================================\n");
}

// ==========================================
// LOGIKA 6: OPM - MENAMBAH FITUR ALAT (ADD-TOOL)
// ==========================================
function addUniversalTool() {
    let id = "", name = "", cmd = "", category = "", description = "", endpoint = "", accepts = "";
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--id') id = args[i + 1];
        if (args[i] === '--name') name = args[i + 1];
        if (args[i] === '--cmd') cmd = args[i + 1];
        if (args[i] === '--category') category = args[i + 1];
        if (args[i] === '--desc') description = args[i + 1];
        if (args[i] === '--endpoint') endpoint = args[i + 1];
        if (args[i] === '--accepts') accepts = args[i + 1];
    }
    
    if (!id || !name || !cmd) {
        console.error('❌ Argumen tidak lengkap! Format: omni add-tool --id \"...\" --name \"...\" --cmd \"...\"');
        process.exit(1);
    }
    
    // 1. Update CLI Registry (Execution Logic)
    const cliRegistryPath = join(ROOT_DIR, 'configs', 'cli_registry.json');
    if (existsSync(cliRegistryPath)) {
        const registry = JSON.parse(readFileSync(cliRegistryPath, 'utf8'));
        const binaryMatch = cmd.trim().split(' ')[0];
        const cmdArgs = cmd.substring(binaryMatch.length).trim().split(' ').filter(a => a);
        
        registry.tools[id] = {
            binary: binaryMatch,
            args: cmdArgs.map(a => a.replace(/"/g, '')),
            timeout_mins: 30
        };
        writeFileSync(cliRegistryPath, JSON.stringify(registry, null, 2));
        console.log(`✅ CLI Registry diperbarui.`);
    }

    // 2. Update OMNI Registry (Metadata UI)
    const omniRegistryPath = join(ROOT_DIR, 'configs', 'registry_omni.json');
    if (existsSync(omniRegistryPath)) {
        const registry = JSON.parse(readFileSync(omniRegistryPath, 'utf8'));
        
        // Cek duplikat
        if (!registry.tools.find(t => t.id === id)) {
            registry.tools.push({
                id,
                category: category || 'CONVERTER',
                name,
                description: description || `Eksekusi ${name}`,
                endpoint: endpoint || `/api/v1/tools/universal/execute`,
                accepts: accepts || '*/*',
                delegateTo: 'C++',
                extraInputs: []
            });
            writeFileSync(omniRegistryPath, JSON.stringify(registry, null, 2));
            console.log(`✅ OMNI Registry diperbarui.`);
        }
    }

    // 3. Trigger Evolve (Auto-generate code)
    evolveCodebase();
    
    console.log(`🎉 SUKSES! Fitur ${name} siap digunakan. (Hukum Sinkronisasi Suci Terpenuhi)`);
}

// ==========================================
// LOGIKA 6.1: OMNI-SYNTHESIZER (CODE GEN)
// ==========================================
function evolveCodebase() {
    console.log("\n🧬 OMNI-SYNTHESIZER: Menginstansi ulang codebase...");
    
    const omniRegPath = join(ROOT_DIR, 'configs', 'registry_omni.json');
    const cliRegPath = join(ROOT_DIR, 'configs', 'cli_registry.json');
    const toolsMapPath = join(ROOT_DIR, 'ui', 'src', 'configs', 'toolsMap.ts');
    
    if (!existsSync(omniRegPath) || !existsSync(cliRegPath) || !existsSync(toolsMapPath)) {
        console.error("❌ Registry atau ToolsMap tidak ditemukan!");
        return;
    }
    
    const omniReg = JSON.parse(readFileSync(omniRegPath, 'utf8'));
    const cliReg = JSON.parse(readFileSync(cliRegPath, 'utf8'));
    
    const cliTools = cliReg.tools || {};
    const metadataMap = new Map();
    (omniReg.tools || []).forEach(t => metadataMap.set(t.id, t));

    let generatedCode = '';
    let currentCategory = 'CONVERTER';
    let syncCount = 0;

    const iconMap = {
        'VIDEO': 'Video',
        'AUDIO': 'Mic',
        'IMAGE': 'Image',
        'PDF': 'FileText',
        'CONVERTER': 'ArrowRightLeft',
        'AI': 'Sparkles',
        'LLM': 'Bot',
        'SYSTEM': 'Box'
    };

    Object.keys(cliTools).forEach(key => {
        if (typeof cliTools[key] === 'string' && (key.startsWith('_CATEGORY_') || key.includes('===='))) {
            const catContent = cliTools[key].toLowerCase();
            if (catContent.includes('video')) currentCategory = 'VIDEO';
            else if (catContent.includes('audio')) currentCategory = 'AUDIO';
            else if (catContent.includes('image')) currentCategory = 'IMAGE';
            else if (catContent.includes('pdf')) currentCategory = 'PDF';
            else if (catContent.includes('converter')) currentCategory = 'CONVERTER';
            else if (catContent.includes('ai') || catContent.includes('llm')) currentCategory = 'LLM';
            return;
        }

        if (key.startsWith('_') || key.includes('====')) return;

        const id = key;
        const metadata = metadataMap.get(id) || {
            name: id.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
            description: `Tool eksekusi otomatis untuk ${id}`,
            category: currentCategory,
            accepts: id.includes('video') ? '.mp4, .mkv' : id.includes('audio') ? '.mp3, .wav' : '*/*',
            endpoint: `/api/v1/tools/${currentCategory.toLowerCase()}/execute`
        };
        
        const iconName = iconMap[metadata.category || currentCategory] || 'Box';

        generatedCode += `  { 
    id: '${id}', 
    name: '${metadata.name}', 
    description: '${(metadata.description || '').replace(/'/g, "\\'")}', 
    category: '${metadata.category || currentCategory}', 
    accepts: '${metadata.accepts}',
    icon: ${iconName},
    endpoint: '${metadata.endpoint}',
    extraInputs: ${JSON.stringify(metadata.extraInputs || [])}
  },\n`;
        syncCount++;
    });
    
    let tsContent = readFileSync(toolsMapPath, 'utf8');
    const startTag = '// @omni-gen-start';
    const endTag = '// @omni-gen-end';
    
    const startIndex = tsContent.indexOf(startTag);
    const endIndex = tsContent.indexOf(endTag);
    
    if (startIndex === -1 || endIndex === -1) {
        console.error("❌ Tag generator (@omni-gen-start/end) tidak ditemukan di toolsMap.ts!");
        return;
    }
    
    const startPos = startIndex + startTag.length;
    
    const newContent = tsContent.substring(0, startPos) + '\n' + generatedCode + '  ' + tsContent.substring(endIndex);
    writeFileSync(toolsMapPath, newContent);
    
    console.log(`✅ Berhasil menyinkronkan ${syncCount} alat ke UI (toolsMap.ts).`);
}

// ==========================================
// 🪡 THE AUTO-HEALER: MASS UI SYNCHRONIZER
// ==========================================
function healFrontendSync(registry, tsMapPath) {
    console.log("   ↳ 🪡 [AUTO-HEAL] Menjahit ulang antarmuka UI secara massal...");
    
    let uiMapContent = `// 🧬 GENERATED & HEALED BY OMNI SYSTEM (Do not edit manually)\n`;
    uiMapContent += `import { LucideIcon, Video, Mic, Image, FileText, ArrowRightLeft, Sparkles, Box, Bot } from 'lucide-react';\n\n`;
    uiMapContent += `export type OmniCategory = 'VIDEO' | 'AUDIO' | 'IMAGE' | 'PDF' | 'CONVERTER' | 'AI' | 'LLM' | 'SYSTEM';\n`;
    uiMapContent += `export interface OmniToolUI { 
    id: string; 
    name: string; 
    description: string; 
    category: OmniCategory; 
    accepts: string; 
    icon: LucideIcon;
    requiresInput?: { key: string; label: string; type: 'text' | 'password' }[]; 
    endpoint?: string; 
    extraInputs?: any[];
}\n\n`;
    uiMapContent += `export const OMNI_TOOLS_UI: OmniToolUI[] = [\n`;

    const iconMap = {
        'VIDEO': 'Video',
        'AUDIO': 'Mic',
        'IMAGE': 'Image',
        'PDF': 'FileText',
        'CONVERTER': 'ArrowRightLeft',
        'AI': 'Sparkles',
        'LLM': 'Bot',
        'SYSTEM': 'Box'
    };

    // Loop semua fitur di Backend dan buatkan UI-nya
    const tools = registry.tools || {};
    for (const [id, cfg] of Object.entries(tools)) {
        if (id.startsWith('_') || id.includes('====')) continue;

        let category = 'SYSTEM';
        if (id.startsWith('video_')) category = 'VIDEO';
        else if (id.startsWith('audio_')) category = 'AUDIO';
        else if (id.startsWith('image_') || id.startsWith('img_')) category = 'IMAGE';
        else if (id.startsWith('pdf_')) category = 'PDF';
        else if (id.startsWith('ai_') || id.startsWith('llm_')) category = 'AI';
        else if (id.startsWith('conv_')) category = 'CONVERTER';

        const prettyName = id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        uiMapContent += `  { 
    id: '${id}', 
    name: '${prettyName}', 
    description: 'Auto-generated interface for ${cfg.binary || id}', 
    category: '${category}', 
    accepts: '${category.toLowerCase()}/*' 
  },\n`;
    }

    uiMapContent += `];\n`;
    
    // Tulis ulang file secara paksa
    writeFileSync(tsMapPath, uiMapContent, 'utf8');
    console.log("   ↳ ✅ [AUTO-HEAL] Sinkronisasi UI berhasil 100%!");
}

// ==========================================
// 👁️ THE EYE OF OMNI: MASS DEBUGGING & DIAGNOSTICS
// ==========================================
function runDeepDiagnostics() {
    console.log("\n👁️ [THE EYE OF OMNI] Memulai Pemindaian Infrastruktur Total...");
    console.log("Menganalisis anomali lintas dimensi (UI, API, Registry)...\n");

    let massErrors = []; // Keranjang Penampung Error Massal
    let totalChecks = 0;

    // ---------------------------------------------------------
    // 🛡️ TAHAP 1: ANALISIS SINKRONISASI (JSON vs TYPESCRIPT)
    // ---------------------------------------------------------
    console.log("⏳ Menganalisis Sinkronisasi 150+ Fitur...");
    try {
        totalChecks++;
        const registryPath = join(ROOT_DIR, 'configs/cli_registry.json');
        const tsMapPath = join(ROOT_DIR, 'ui/src/configs/toolsMap.ts');
        
        if (!existsSync(registryPath) || !existsSync(tsMapPath)) {
            throw new Error("File Registry atau UI Map tidak ditemukan.");
        }

        const registry = JSON.parse(readFileSync(registryPath, 'utf8'));
        const tsMapCode = readFileSync(tsMapPath, 'utf8');

        let isDesynced = false;

        // Registry OMNI bisa berupa array [{id: '...'}, ...] atau object {id: {...}}
        const toolsRaw = registry.tools || {};
        const toolIds = Object.keys(toolsRaw).filter(id => !id.startsWith('_') && !id.includes('===='));

        for (const toolId of toolIds) {
            // Regex untuk mencari ID persis di file TS (string literal format)
            const idRegex = new RegExp(`id:\\s*['"\\\\\`]${toolId}['"\\\\\`]`);
            if (!idRegex.test(tsMapCode)) {
                isDesynced = true;
                break;
            }
        }

        // JIKA TERJADI SYNC FATAL -> LANGSUNG PERBAIKI!
        if (isDesynced) {
            console.log(`⚠️ [SYNC FATAL] Terdeteksi fitur Backend yang belum memiliki tombol di UI!`);
            healFrontendSync(registry, tsMapPath);
        } else {
            console.log("✅ Sinkronisasi UI dan Backend Aman.");
        }

    } catch (e) {
        massErrors.push(`[FILE FATAL] Gagal membaca file registry atau UI Map. Detail: ${e.message}`);
    }

    // ---------------------------------------------------------
    // 🎨 TAHAP 2: ANALISIS FRONTEND (TYPE CHECKING)
    // ---------------------------------------------------------
    console.log("⏳ Menganalisis Integritas JSX/TypeScript...");
    totalChecks++;
    try {
        // tsc --noEmit akan mengecek SELURUH error syntax/tipe data di React
        execSync('npx tsc --noEmit', { cwd: join(ROOT_DIR, 'ui'), stdio: 'pipe' });
    } catch (e) {
        // Tangkap seluruh output error dari TypeScript
        const tsErrors = e.stdout.toString().split('\n').filter(line => line.includes('error TS'));
        tsErrors.forEach(err => massErrors.push(`[UI ERROR] ${err.trim()}`));
    }

    // ---------------------------------------------------------
    // 🐹 TAHAP 3: ANALISIS BACKEND (GO VET & BUILD TEST)
    // ---------------------------------------------------------
    console.log("⏳ Menganalisis Kestabilan Arsitektur Golang...");
    totalChecks++;
    try {
        // go vet mencari kode Go yang valid secara syntax tapi memiliki bug logika
        execSync('go vet ./...', { cwd: join(ROOT_DIR, 'api'), stdio: 'pipe' });
        // go build dengan flag -n hanya mengecek apakah bisa dicompile
        execSync('go build -v -n ./...', { cwd: join(ROOT_DIR, 'api'), stdio: 'pipe' });
    } catch (e) {
        const output = (e.stderr || e.stdout || "").toString();
        const goErrors = output.split('\n').filter(line => line.trim() !== '');
        goErrors.forEach(err => {
            if (err.includes('.go:')) massErrors.push(`[API ERROR] ${err.trim()}`);
        });
    }

    // ---------------------------------------------------------
    // 🔮 TAHAP 4: OMNI-ORACLE (GHOST API & LOGIC FUZZ)
    // ---------------------------------------------------------
    console.log("⏳ Mengaktifkan OMNI-ORACLE (Ghost API & Logic Protection)...");
    totalChecks += 2;
    try {
        // Run API Ghost Handler
        execSync('node bin/oracle_api.mjs', { cwd: ROOT_DIR, stdio: 'inherit' });
        console.log("✅ [ORACLE] Dimension 1: API Ghost Healing Aktif.");

        // Run Logic Fuzz Guardian
        execSync('node bin/oracle_logic.mjs', { cwd: ROOT_DIR, stdio: 'inherit' });
        console.log("✅ [ORACLE] Dimension 3: Logic Fuzz Protection Aktif.");
    } catch (e) {
        massErrors.push(`[ORACLE FATAL] Gagal dalam diagnosa Oracle: ${e.message}`);
    }

    // ---------------------------------------------------------
    // 🚨 HASIL PEMINDAIAN MASSAL (THE VERDICT)
    // ---------------------------------------------------------
    console.log("\n========================================================");
    if (massErrors.length === 0) {
        console.log(`✅ [STATUS: PERFECT] ${totalChecks} Sektor Utama Bebas Anomali.`);
        console.log("🚀 OMNI TOOLS SIAP DILUNCURKAN TANPA CACAT.");
        return true;
    } else {
        console.log(`❌ [STATUS: CRITICAL] Ditemukan ${massErrors.length} Kerusakan Massal!`);
        console.log("========================================================\n");
        
        // Cetak semua error berurutan seperti laporan militer
        massErrors.forEach((error, index) => {
            console.log(`${index + 1}. ${error}`);
        });

        console.log("\n🛑 PELUNCURAN SERVER DIBATALKAN. HARAP PERBAIKI DAFTAR ANOMALI DI ATAS.");
        process.exit(1); // Hentikan sistem seketika
    }
}

// ==========================================
// LOGIKA 7: OMNI DOCTOR (SELF-HEALING)
// ==========================================
async function runOmniDoctor() {
    console.log("\n🩺 OMNI DOCTOR: Memulai pemeriksaan kesehatan sistem...\n");

    await checkDependencies();

    try {
        // 1. REPARASI UI (React/TS/JSX)
        console.log("\n🎨 [UI] Memperbaiki ESLint & Prettier...");
        execSync('npx eslint --fix "src/**/*.{ts,tsx}" || echo "ESLint done with warnings"', { cwd: join(ROOT_DIR, 'ui'), stdio: 'inherit', shell: true });
        console.log("✅ UI berhasil dirapikan.");

        // 2. REPARASI API (Golang)
        console.log("\n🐹 [API] Menjalankan Gofmt (Standardizing Go Code)...");
        execSync('go fmt ./...', { cwd: join(ROOT_DIR, 'api'), stdio: 'inherit' });
        console.log("✅ Kode Golang berhasil distandarisasi.");

        // 3. REPARASI ENGINE (C++)
        console.log("\n⚙️  [ENGINE] Merapikan sintaks C++ (Clang-Format)...");
        try {
            const cppFiles = findFilesRecursive(join(ROOT_DIR, 'engine'), ['.cpp', '.h', '.hpp']);
            if (cppFiles.length > 0) {
                execSync(`clang-format -i ${cppFiles.join(' ')}`, { stdio: 'inherit' });
                console.log(`✅ ${cppFiles.length} file Engine C++ berhasil dipercantik.`);
            } else {
                console.log("ℹ️  Tidak ditemukan file C++ untuk diperbaiki.");
            }
        } catch (e) {
            console.log("⚠️  Clang-format gagal atau tidak ditemukan. Melewati reparasi C++.");
        }

        // 4. VALIDASI CONFIG (JSON)
        validateRegistry();

        console.log("\n🚀 OMNI TOOLS KEMBALI PRIMA! Sistem imun aktif.");

    } catch (error) {
        console.error("\n❌ OMNI DOCTOR menemukan kerusakan yang butuh campur tangan manusia.");
        console.error(error.message);
    }
}

async function checkDependencies(silent = false) {
    const missing = await getMissingDependencies(silent);

    if (missing.length > 0) {
        console.log(`\n🛡️ OMNI DOCTOR: Menemukan ${missing.length} senjata yang absen.`);
        console.log("👉 Untuk menginstal otomatis, jalankan: omni install bin");
    }
}

async function getMissingDependencies(silent = false) {
    const deps = [
        { id: 'ffmpeg', name: 'FFmpeg', cmd: 'ffmpeg -version', url: 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' },
        { id: 'golang', name: 'Golang', cmd: 'go version' },
        { id: 'node', name: 'Node.js', cmd: 'node -v' },
        { id: 'magick', name: 'ImageMagick', cmd: 'magick -version', url: 'https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-30-portable-Q16-x64.zip' },
        { id: 'pandoc', name: 'Pandoc', cmd: 'pandoc -v', url: 'https://github.com/jgm/pandoc/releases/download/3.1.12.3/pandoc-3.1.12.3-windows-x86_64.zip' },
        { id: 'clang-format', name: 'ClangFormat', cmd: 'clang-format --version', url: 'https://github.com/llvm/llvm-project/releases/download/llvmorg-17.0.6/LLVM-17.0.6-win64.exe' }
    ];

    const missing = [];
    if (!silent) console.log("🔍 Mengecek Ketersediaan Senjata Perang...");
    
    deps.forEach(dep => {
        try {
            execSync(dep.cmd, { stdio: 'ignore' });
            if (!silent) console.log(`✅ ${dep.name}: TERPASANG`);
        } catch (e) {
            if (!silent) console.log(`❌ ${dep.name}: TIDAK DITEMUKAN`);
            if (dep.url) missing.push(dep);
        }
    });

    return missing;
}

// runAutoInstall dan downloadFileWithProgress tetap ada sebagai referensi 
// tapi tidak dipanggil otomatis agar user bisa download sendiri.

async function runAutoInstall(deps) {
    console.log("\n🚀 Memulai OMNI AUTO-INSTALLER ENGINE (v2.3 - Heavy Duty)...");
    
    for (const dep of deps) {
        const zipFile = join(OMNI_BIN, `${dep.id}.zip`);
        console.log(`\n📥 Downloading ${dep.name} via PowerShell...`);
        
        try {
            // Hapus sisa kegagalan sebelumnya
            if (existsSync(zipFile)) execSync(`del "${zipFile}"`, { shell: true });
            
            // Gunakan Invoke-WebRequest (Lebih stabil di Windows)
            const downloadCmd = `powershell.exe -Command "$ProgressPreference = 'Continue'; Invoke-WebRequest -Uri '${dep.url}' -OutFile '${zipFile}'"`;
            execSync(downloadCmd, { stdio: 'inherit' });

            console.log(`📦 Extracting ${dep.name}...`);
            const extractCmd = `powershell.exe -Command "$ErrorActionPreference = 'Stop'; Expand-Archive -Path '${zipFile}' -DestinationPath '${OMNI_BIN}' -Force"`;
            execSync(extractCmd, { stdio: 'inherit' });
            
            // Berishkan zip
            execSync(`del "${zipFile}"`, { shell: true });
            
            // LOGIKA PENTING: Flattening (Pindahkan .exe ke akar bin/)
            flattenBinFolder(OMNI_BIN);
            
            console.log(`✅ ${dep.name} Berhasil diinstal dan disinkronisasi!`);
        } catch (err) {
            console.error(`❌ Gagal menginstal ${dep.name}: ${err.message}`);
        }
    }
    
    console.log("\n🎉 SEMUA SENJATA TELAH SIAP! Jalankan 'omni fix' lagi untuk verifikasi akhir.");
}

function flattenBinFolder(binDir) {
    const files = findFilesRecursive(binDir, ['.exe', '.dll']);
    files.forEach(file => {
        const fileName = file.split(/[\\/]/).pop();
        const targetPath = join(binDir, fileName);
        if (file !== targetPath) {
            try {
                // Gunakan copy + unlink agar lebih aman lintas drive jika perlu
                execSync(`copy /Y "${file}" "${targetPath}"`, { stdio: 'ignore', shell: true });
            } catch (e) {}
        }
    });

    // Opsional: Hapus folder kosong atau folder versi agar bin/ tetap bersih
    // (Aman dibiarkan karena .exe sudah di akar)
}

// downloadFileWithProgress dihapus karena digantikan PowerShell Invoke-WebRequest
// tapi tetap buat skeleton agar tidak error jika dipanggil tempat lain
function downloadFileWithProgress(url, dest, label) {
    console.log(`⚠️ Legacy downloader called for ${label}. Redirecting to PowerShell...`);
    const downloadCmd = `powershell.exe -Command "Invoke-WebRequest -Uri '${url}' -OutFile '${dest}'"`;
    execSync(downloadCmd, { stdio: 'inherit' });
    return Promise.resolve();
}

function validateRegistry() {
    console.log("\n📄 [CONFIG] Memvalidasi struktur cli_registry.json...");
    const registryPath = join(ROOT_DIR, 'configs/cli_registry.json');
    if (!existsSync(registryPath)) return;

    try {
        const registry = JSON.parse(readFileSync(registryPath, 'utf8'));
        const toolIds = Object.keys(registry.tools || {});
        
        // Deteksi ID duplikat atau struktur rusak
        const seen = new Set();
        const duplicates = toolIds.filter(id => seen.has(id) || !seen.add(id));
        
        if (duplicates.length > 0) {
            console.log(`⚠️  Ditemukan ID duplikat: ${duplicates.join(', ')}`);
        } else {
            console.log(`✅ Validasi selesai: ${toolIds.length} Tools terverifikasi aman.`);
        }
    } catch (e) {
        console.log("❌ cli_registry.json KORUP atau Salah Format JSON!");
    }
}

// Utility: Lintas Platform Recursive File Search
function findFilesRecursive(dir, extensions) {
    let results = [];
    if (!existsSync(dir)) return results;
    
    const list = readdirSync(dir);
    list.forEach(file => {
        const fullPath = join(dir, file);
        const stat = lstatSync(fullPath);
        if (stat && stat.isDirectory()) {
            results = results.concat(findFilesRecursive(fullPath, extensions));
        } else {
            if (extensions.some(ext => fullPath.endsWith(ext))) {
                results.push(fullPath);
            }
        }
    });
    return results;
}

// ==========================================
// 🦎 TAHAP 10: OMNI CHAMELEON (UNIVERSAL UI DICTIONARY)
// ==========================================
function changeTheme(themeName) {
    const UI_DICTIONARY = {
        layout: {
            tailwind: 'min-h-screen bg-background text-foreground flex overflow-hidden',
            bootstrap: 'd-flex vh-100 overflow-hidden bg-dark text-light',
            bulma: 'is-flex is-flex-direction-row' // with custom vh-100 css
        },
        sidebar: {
            tailwind: 'w-64 border-r border-white/10 bg-black/50 backdrop-blur-md flex flex-col',
            bootstrap: 'd-flex flex-column flex-shrink-0 p-3 bg-black border-end border-secondary',
            bulma: 'menu p-4 has-background-black has-border-right'
        },
        navItem: {
            tailwind: 'flex items-center gap-3 px-4 py-3 rounded-xl transition-all',
            bootstrap: 'nav-link d-flex align-items-center gap-3 py-3 px-4 rounded',
            bulma: 'is-flex is-align-items-center px-4 py-3'
        },
        navItemActive: {
            tailwind: 'bg-primary/20 text-primary font-bold shadow-[0_0_15px_rgba(var(--primary),0.3)]',
            bootstrap: 'active bg-primary text-white font-weight-bold shadow',
            bulma: 'is-active has-background-primary-light has-text-primary has-text-weight-bold'
        },
        card: {
            tailwind: 'group relative p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-primary/50 transition-all cursor-pointer',
            bootstrap: 'card bg-dark border border-secondary p-4 h-100 cursor-pointer shadow-hover',
            bulma: 'box has-background-black-bis has-border-danger cursor-pointer'
        },
        button: {
            tailwind: 'w-full py-4 bg-primary text-primary-foreground font-black rounded-xl hover:bg-primary/90 flex items-center justify-center gap-2',
            bootstrap: 'btn btn-primary w-100 py-3 fw-bold d-flex align-items-center justify-content-center gap-2',
            bulma: 'button is-primary is-fullwidth is-medium has-text-weight-bold'
        },
        input: {
            tailwind: 'flex h-12 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors',
            bootstrap: 'form-control bg-dark text-light border-secondary p-3',
            bulma: 'input is-medium has-background-black has-text-white'
        }
    };
    
    const CDNS = {
        tailwind: '', // Native / included via CSS
        bootstrap: '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">\n    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>',
        bulma: '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css">',
        foundation: '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/foundation/6.8.1/css/foundation.min.css">\n    <script src="https://cdnjs.cloudflare.com/ajax/libs/foundation/6.8.1/js/foundation.min.js"></script>',
        semantic: '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.5.0/semantic.min.css">\n    <script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.5.0/semantic.min.js"></script>'
    };

    if (!themeName) {
        console.error("❌ Nama framework tidak boleh kosong! (tailwind/bootstrap/bulma/foundation/semantic)");
        process.exit(1);
    }
    const theme = themeName.toLowerCase();
    if (!CDNS.hasOwnProperty(theme)) {
        console.error(`❌ Tema '${theme}' tidak dikenali. Pilih: tailwind, bootstrap, bulma, foundation, semantic.`);
        process.exit(1);
    }

    console.log(`\n🦎 [OMNI CHAMELEON] Mengaktifkan Transformasi Tema: ${theme.toUpperCase()}`);

    // 1. Ganti CDN di index.html
    const indexPath = join(ROOT_DIR, 'ui', 'index.html');
    if (existsSync(indexPath)) {
        let html = readFileSync(indexPath, 'utf8');
        // Hapus CDN lama (magic comment marker)
        html = html.replace(/<!-- CHAMELEON_CDN -->[\s\S]*?<!-- \/CHAMELEON_CDN -->/, '');
        
        let newCDN = '';
        if (theme !== 'tailwind') {
            newCDN = `<!-- CHAMELEON_CDN -->\n    ${CDNS[theme]}\n    <!-- /CHAMELEON_CDN -->`;
        }
        
        // Inject diatas </head>
        html = html.replace('</head>', `${newCDN}\n  </head>`);
        writeFileSync(indexPath, html, 'utf8');
        console.log(`   ↳ 🌐 index.html berhasil diinjeksi dengan ${theme.toUpperCase()}`);
    }

    // 2. Generate Provider/Config UI
    const themeConfigPath = join(ROOT_DIR, 'ui', 'src', 'configs', 'chameleon.ts');
    let themeConfig = `// 🦎 GENERATED BY OMNI CHAMELEON\n`;
    themeConfig += `export const ACTIVE_THEME = '${theme}';\n\n`;
    themeConfig += `export const CHAMELEON_UI = ${JSON.stringify(UI_DICTIONARY, null, 2)};\n`;
    
    // Tulis ke chameleon.ts yang akan dipakai oleh komponen React untuk mapping kelas CSS
    writeFileSync(themeConfigPath, themeConfig, 'utf8');
    console.log(`   ↳ 🎨 Kamus Kosmetik tersimpan di chameleon.ts`);

    // 3. Modifikasi UI Utama secara "Cerdas" (jika perlu)
    // Sebagai bukti konsep tingkat lanjut, kita bisa merubah file jika mereka tak terhubung ke chameleon.
    // Saat ini, dengan chameleon.ts, React dapat membaca CHAMELEON_UI[komponen][ACTIVE_THEME] dll.

    console.log(`\n✅ Transformasi selesai! Komponen UI kini menggunakan kelas dari ${theme.toUpperCase()}.`);
    console.log(`➡️  Mulai ulang Vite dengan 'omni dev' untuk melihat perubahan.\n`);
}

// ==========================================
// 🛡️ OMNI-GUARD: ROLE ISOLATION ENFORCER
// ==========================================
function enforceRoleIsolation() {
    console.log("🛡️ [OMNI-GUARD] Memeriksa Pelanggaran Wilayah Kekuasaan...");
    
    let violationFound = false;

    function walkDir(dir, regex) {
        let results = [];
        if (!existsSync(dir)) return results;
        const list = readdirSync(dir);
        list.forEach(file => {
            if (file === 'node_modules' || file === '.git') return; // Abaikan third-party dan git
            const filePath = join(dir, file);
            const stat = lstatSync(filePath);
            if (stat && stat.isDirectory()) {
                results = results.concat(walkDir(filePath, regex));
            } else {
                if (regex.test(file)) results.push(filePath);
            }
        });
        return results;
    }

    // Aturan 1: Tidak boleh ada file .go di folder /ui
    const uiGoFiles = walkDir(join(ROOT_DIR, 'ui'), /\.go$/);
    if (uiGoFiles.length > 0) {
        console.error("❌ PELANGGARAN: Ditemukan file Golang di wilayah Frontend (/ui)!");
        console.error(`   Contoh: ${uiGoFiles[0]}`);
        violationFound = true;
    }

    // Aturan 2: Tidak boleh ada file .js/.tsx di folder /api
    const apiJsFiles = walkDir(join(ROOT_DIR, 'api'), /\.(js|tsx)$/);
    if (apiJsFiles.length > 0) {
        console.error("❌ PELANGGARAN: Ditemukan file React/JS di wilayah Backend (/api)!");
        console.error(`   Contoh: ${apiJsFiles[0]}`);
        violationFound = true;
    }

    if (violationFound) {
        console.error("⚠️ [OMNI-GUARD] Disiplin Arsitektur Dilanggar! Kompilasi digagalkan.");
        process.exit(1);
    } else {
        console.log("✅ [OMNI-GUARD] Disiplin Arsitektur Terjaga. Melanjutkan kompilasi...");
    }
}

// ==========================================
// 🔨 TAHAP 11: OMNI-FORGE (PABRIK SENJATA OTOMATIS)
// ==========================================
function runOmniForge(name) {
    if (!name) {
        console.error("❌ Nama fitur harus diberikan! Contoh: omni make tool image_blur");
        process.exit(1);
    }

    const camelName = name.replace(/_([a-z])/g, g => g[1].toUpperCase());
    
    // 1. GENERATE BACKEND GOLANG (Terisolasi dari Frontend)
    const goPath = join(ROOT_DIR, `api/engine/worker_${name}.go`);
    const goCode = `package engine

import "omnitools/core"

// Process${camelName} adalah logika untuk fitur ${name}.
// Skuad Backend: Fokus di sini! Jangan pikirkan UI.
func Process${camelName}(job *core.Job) error {
    inputPath := ""
    outputPath := ""
    if len(job.Args) >= 2 {
        inputPath = job.Args[0]
        outputPath = job.Args[1]
    }
    // Gunakan Blackbox Engine agar Anda tidak perlu menyentuh C++
    return RunHeavyEngine("${name}", inputPath, outputPath)
}
`;
    const engineDir = dirname(goPath);
    if (!existsSync(engineDir)) mkdirSync(engineDir, { recursive: true });
    writeFileSync(goPath, goCode);

    // 2. GENERATE FRONTEND REACT (Terisolasi dari Backend)
    const reactPath = join(ROOT_DIR, `ui/src/tools/${camelName}.tsx`);
    const reactCode = `import React, { useState } from 'react';
import { useOmniJob } from '../hooks/useOmniJob';
import { OmniClient } from '@omni-os/client'; // Menggunakan SDK OMNI!

// Skuad Frontend: Fokus di sini! Backend sudah diurus otomatis.
export default function ${camelName}UI() {
    const [file, setFile] = useState(null);
    const [jobId, setJobId] = useState(null);
    const { progress, status } = useOmniJob(jobId); // Hook otomatis ke WebSocket

    const handleExecute = async () => {
        if (!file) return;
        // Panggil SDK, tak perlu pusing soal fetch, FormData, atau Headers!
        const result = await OmniClient.processFile("${name}", file);
        setJobId(result.job_id);
    };

    return (
        <div className="p-4 bg-gray-800 rounded">
            <h2 className="text-xl font-bold">${name.toUpperCase()}</h2>
            <input type="file" onChange={e => setFile(e.target.files?.[0])} />
            <button onClick={handleExecute} className="bg-blue-500 p-2 mt-2">Eksekusi</button>
            <p>Status: {status} | Progress: {progress}%</p>
        </div>
    );
}
`;
    const reactDir = dirname(reactPath);
    if (!existsSync(reactDir)) mkdirSync(reactDir, { recursive: true });
    writeFileSync(reactPath, reactCode);
    console.log(`✅ [OMNI-FORGE] Skuad Frontend & Backend berhasil dipersenjatai untuk fitur ${name}!`);
}
