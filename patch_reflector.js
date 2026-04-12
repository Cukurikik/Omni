const fs = require('fs');

const content = fs.readFileSync('bin/omni.mjs', 'utf8');

const injection = `
    // 0.5 Spawning Universal UAST Reflector (AUTO-LOADER 645 PACKAGES)
    console.log("\\n🔌 [OMNI-REFLECTOR] Memicu UAST Daemon...");
    const reflectorProcess = spawn('node', ['omni-runtime/telepathy_reflector.mjs'], {
        cwd: ROOT_DIR,
        stdio: 'inherit',
        shell: true
    });
`;

if (content.includes('const reflectorProcess = spawn')) {
    console.log("Reflector sudah tersuntik sebelumnya.");
    process.exit(0);
}

const target = "// 1. Spawning Rust MPSC Engine (omni-core dev)!";
if (content.includes(target)) {
    const newStr = content.replace(target, injection + "\\n    " + target);
    
    // Patch bagian shutdown
    const shutdownTarget = "if (rustProcess) rustProcess.kill();";
    const newStr2 = newStr.replace(shutdownTarget, "if (reflectorProcess) reflectorProcess.kill();\\n        " + shutdownTarget);
    
    fs.writeFileSync('bin/omni.mjs', newStr2, 'utf8');
    console.log('Berhasil menyuntikkan Reflector Engine ke startDevServer!');
} else {
    console.error('Target injeksi tidak ditemukan!');
    process.exit(1);
}
