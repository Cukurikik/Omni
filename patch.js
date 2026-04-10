const fs = require('fs');
const content = fs.readFileSync('bin/omni.mjs', 'utf8');

const newDevServer = \
async function startDevServer() {
    console.log("\\n==========================================");
    console.log("? OMNI-PRIME DEV ORCHESTRATOR — PHASE 19 IGNITION");
    console.log("==========================================");
    console.log("   Engine     : Native Rust Core (JIT Hot-Swap)");
    console.log("   Vite HMR   : Synced via Universal Bridge");
    console.log("   Watcher    : High-Speed Syscall NativeWatcher");
    console.log("==========================================\\n");

    const rustCoreDir = join(ROOT_DIR, 'omni-runtime', 'core');
    const binName = process.platform === 'win32' ? 'omni-core-test.exe' : 'omni-core-test';
    const rustTarget = join(rustCoreDir, 'target', 'debug', binName);
    
    // Pastikan binary Rust sudah ada
    if (!existsSync(rustTarget)) {
        console.log("?? [OMNI-CORE] Binary Rust belum dicompile! Mengompilasi engine... (Harap tunggu)");
        try {
            execSync('cargo build', { cwd: rustCoreDir, stdio: 'inherit' });
        } catch (e) {
            console.error("? [FATAL] Gagal mengompilasi OMNI Core Engine.");
            process.exit(1);
        }
    }

    // 0. BEBASKAN PORT
    console.log("?? Membebaskan jalur komunikasi...");
    liberatePort(3000, "Native JIT Server");
    liberatePort(5173, "Vite Dev Server");

    // 1. Spawning Rust MPSC Engine (omni-core dev)!
    console.log("\\n?? [OMNI-PRIME] Spawning Rust JIT Engine...");
    const rustProcess = spawn(rustTarget, ['dev'], {
        cwd: ROOT_DIR,
        stdio: 'inherit',
        shell: true
    });

    // Tunggu Rust engine siap sebelum Vite
    await new Promise(resolve => setTimeout(resolve, 2000));

    // 2. NYALAKAN VITE FRONTEND (HMR!)
    let viteProcess = null;
    const uiDir = join(ROOT_DIR, 'ui');
    if (existsSync(join(uiDir, 'package.json'))) {
        console.log("\\n? [VITE] Menjalankan Vite Frontend (HMR Mode)...");
        viteProcess = spawn('npm', ['run', 'dev'], {
            cwd: uiDir,
            stdio: 'inherit',
            shell: true, // WAJIB di Windows — npm adalah .cmd batch file
        });

        viteProcess.on('error', (err) => {
            console.error("? [FATAL] Gagal menyalakan Vite.");
            console.error(err.message);
        });
    }

    // 3. TAMPILKAN BATTLESTATION
    console.log("\\n==========================================");
    console.log("?? OMNI-PRIME FULL-STACK AKTIF!");
    console.log("==========================================");
    if (viteProcess) {
        console.log("???  FRONTEND (Vite HMR) : \\x1b[36mhttp://localhost:5173\\x1b[0m");
    }
    console.log("?? BACKEND (Rust Hub)   : http://localhost:3000");
    console.log("?? API Proxy            : http://localhost:5173/api/* ? :3000");
    console.log("?? WebSocket Proxy      : ws://localhost:5173/ws/* ? :3000");
    console.log("???  NATIVE-WATCHER       : Watching src/**/*.rs and api/**/*.go");
    console.log("==========================================");
    console.log("Tekan CTRL+C untuk mematikan semua mesin.\\n");

    // GRACEFUL SHUTDOWN — Matikan semua mesin sekaligus
    const shutdown = () => {
        console.log("\\n?? [SHUTDOWN] Mematikan OMNI-PRIME dan semua subsystem...");
        if (rustProcess) rustProcess.kill();
        if (viteProcess) viteProcess.kill();
        console.log("? Semua mesin dimatikan. Sampai jumpa di dimensi berikutnya, Kapten! ??");
        process.exit();
    };

    process.on('SIGINT', shutdown);
    process.on('SIGTERM', shutdown);
}
\

const targetStart = /^async function startDevServer\(\) \{/m;
const matchStart = content.match(targetStart);
let matchedEnd = -1;

if (matchStart) {
    let braceCount = 0;
    let started = false;
    for (let i = matchStart.index; i < content.length; i++) {
        if (content[i] === '{') {
            braceCount++;
            started = true;
        } else if (content[i] === '}') {
            braceCount--;
            if (started && braceCount === 0) {
                matchedEnd = i;
                break;
            }
        }
    }
    
    if (matchedEnd !== -1) {
        const newStr = content.slice(0, matchStart.index) + newDevServer + content.slice(matchedEnd + 1);
        fs.writeFileSync('bin/omni.mjs', newStr, 'utf8');
        console.log('Successfully replaced startDevServer in bin/omni.mjs');
    } else {
        console.log('Error finding end brace');
    }
} else {
    console.log('Error finding startDevServer function');
}

