// ==========================================
// 🖥️ OMNI DESKTOP TELEMETRY (Phase 59)
// ==========================================

const consoleOutput = document.getElementById('console-output');

const simulatedLogs = [
    "[SYSTEM] UAST Gateway memetakan permintaan baru...",
    "[ROUTER] Ruby DSL mengalihkan paket dari GraphQL Endpoint.",
    "[HFT] Membangkitkan C++ Thread Buffer 0x7FFF...",
    "[PYTHON-ML] Mengoreksi Sinyal Arbitrase. Confidence: 99.4%.",
    "[SECURITY] WAF memukul mundur injeksi nakal pada port 4002.",
    "[GO-BRIDGE] Transmisi Zero-Copy Memory sukses dikumpulkan.",
    "[KUBERNETES] Spawning region asia-southeast-2 untuk komputasi ray."
];

let currentIndex = 0;

function pushLog() {
    if (currentIndex >= simulatedLogs.length) {
        currentIndex = 0; // Loop kembali untuk efek endless
    }

    const logText = simulatedLogs[currentIndex];
    const el = document.createElement('div');
    el.className = 'log-entry';
    
    // Warn styling jika ada kata SECURITY
    if (logText.includes('[SECURITY]')) {
        el.classList.add('log-warn');
    }

    const timestamp = new Date().toISOString().split('T')[1].slice(0, -1);
    el.innerText = `[${timestamp}] ${logText}`;
    
    consoleOutput.appendChild(el);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
    
    currentIndex++;
    
    // Waktu acak antara 500ms hingga 2500ms
    const nextTime = Math.random() * 2000 + 500;
    setTimeout(pushLog, nextTime);
}

// Inisialisasi Kuantum Event Loop
setTimeout(pushLog, 1000);
