// ==========================================
// 🐵 THE MONKEY PATCH: Zero-Trust Injector
// ==========================================
// Skrip ini diinjeksikan secara paksa ke dalam memori 
// Node Parasit maupun Mikro V8 sekejap sebelum 
// kode pengguna berjalan, mematikan fungsi berbahaya.
// ==========================================

pub fn generate_security_preamble(allowed_fs: &[String], allowed_net: &[String]) -> String {
    let mut script = String::new();
    
    script.push_str("
// --- OMNI ZERO-TRUST PREAMBLE START ---
(function() {
    // 1. Sadap Console.log agar tidak mencemari OMNI Terminal
    const originalConsoleLog = console.log;
    console.log = function(...args) {
        // Encode logs using OMNI-IPC format
        originalConsoleLog('[OMNI-IPC-LOG]', ...args);
    };

    // 2. Lumpuhkan Global Objects yang berbahaya
    const poison_pill = () => { throw new Error('🔥 OMNI SECURITY BLACKLIST: Operasi Dilarang!'); };
    
");

    // Jika file sistem dilarang
    if allowed_fs.is_empty() {
        script.push_str("
    // Menonaktifkan Akses Hard Drive
    if (typeof require !== 'undefined') {
        const originalRequire = require;
        require = function(mod) {
            if (mod === 'fs' || mod === 'fs/promises' || mod === 'child_process') {
               poison_pill();
            }
            return originalRequire(mod);
        };
    }
");
    }

    // Jika Network dilarang
    if allowed_net.is_empty() {
        script.push_str("
    // Menonaktifkan Akses Jaringan/Socket
    if (typeof require !== 'undefined') {
        const _req = require;
        require = function(mod) {
            if (mod === 'http' || mod === 'https' || mod === 'net' || mod === 'dgram') {
               poison_pill();
            }
            return _req(mod);
        };
    }
    // Block Native Fetch di lingkungan V8/Node newer versions
    globalThis.fetch = async () => poison_pill();
");
    }

    script.push_str("
})();
// --- OMNI ZERO-TRUST PREAMBLE END ---
");

    script
}
