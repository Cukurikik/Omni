// ==========================================
// 🌍 OMNI-JS STDLIB: Default Index Route
// ==========================================
// File ini adalah handler untuk URL: /
// Auto-loaded oleh OMNI-NET Golang Server.
//
// CARA KERJA:
//   1. Golang membaca file ini dari SSD
//   2. Golang mengirim isinya ke Rust-V8 Sandbox
//   3. V8 mengeksekusi OmniHandler() dengan konteks request
//   4. Hasil dikembalikan ke browser sebagai JSON
// ==========================================

function OmniHandler(req) {
    const data = {
        pesan: "Selamat datang di OMNI-JS Runtime!",
        metode: req.method,
        url: req.url,
        status: "Kedaulatan Mutlak",
        runtime: {
            engine: __OMNI_RUNTIME__,
            version: __OMNI_VERSION__,
            node_js: "TIDAK DIBUTUHKAN ❌"
        },
        timestamp: new Date().toISOString()
    };

    console.log("📡 Request diterima:", req.method, req.url);

    return JSON.stringify(data, null, 2);
}
