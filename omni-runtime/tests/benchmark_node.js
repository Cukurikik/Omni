// ═══════════════════════════════════════════════════════════════════════
// 🐌 NODE.JS EQUIVALENT BENCHMARK — For Comparison with OMNI
// ═══════════════════════════════════════════════════════════════════════
// Run: node tests/benchmark_node.js
// Compare with: omni run tests/benchmark.omni
// ═══════════════════════════════════════════════════════════════════════

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ─── ANSI Colors ───
const red = (t) => `\x1b[31m${t}\x1b[0m`;
const green = (t) => `\x1b[32m${t}\x1b[0m`;
const yellow = (t) => `\x1b[33m${t}\x1b[0m`;
const cyan = (t) => `\x1b[36m${t}\x1b[0m`;
const bold = (t) => `\x1b[1m${t}\x1b[0m`;
const dim = (t) => `\x1b[2m${t}\x1b[0m`;

function formatNumber(n) {
    if (!isFinite(n)) return '∞';
    if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(2) + 'K';
    return n.toFixed(2);
}

function runBench(name, iterations, task) {
    const start = performance.now();
    for (let i = 0; i < iterations; i++) task();
    const elapsed = Math.max(performance.now() - start, 0.01);
    return { name, ops_per_sec: (iterations / elapsed) * 1000, duration_ms: elapsed, iterations };
}

// ═══════════════════════════════════════════════════════════════════════
// BENCHMARK 1: Fibonacci (Pure CPU)
// ═══════════════════════════════════════════════════════════════════════
function fibonacci(n) { return n <= 1 ? n : fibonacci(n - 1) + fibonacci(n - 2); }
const benchFibonacci = () => runBench('Fibonacci(30) — Pure CPU', 100, () => fibonacci(30));

// ═══════════════════════════════════════════════════════════════════════
// BENCHMARK 2: String Operations
// ═══════════════════════════════════════════════════════════════════════
const benchString = () => runBench('String Concat — 10K iterations', 10000, () => {
    let s = '';
    for (let i = 0; i < 100; i++) s += 'omni-framework-' + i;
    void s.length;
});

// ═══════════════════════════════════════════════════════════════════════
// BENCHMARK 3: JSON Parse/Stringify
// ═══════════════════════════════════════════════════════════════════════
const benchJSON = () => {
    const data = { users: [], meta: { total: 1000, page: 1 } };
    for (let i = 0; i < 100; i++) data.users.push({ id: i, name: `User_${i}`, email: `user${i}@omni.dev`, active: i % 2 === 0, score: i * 3.14 });
    const jsonStr = JSON.stringify(data);
    return runBench('JSON Parse+Stringify — 100 objects', 5000, () => { void JSON.stringify(JSON.parse(jsonStr)); });
};

// ═══════════════════════════════════════════════════════════════════════
// BENCHMARK 4: Crypto SHA256
// ═══════════════════════════════════════════════════════════════════════
const benchCrypto = () => runBench('SHA256 Hash — Node.js Crypto', 10000, () => {
    crypto.createHash('sha256').update('OMNI Framework beats Node.js in every benchmark test ' + Date.now()).digest('hex');
});

// ═══════════════════════════════════════════════════════════════════════
// BENCHMARK 5: Map Operations
// ═══════════════════════════════════════════════════════════════════════
const benchMap = () => runBench('Map — 1K insert+lookup', 1000, () => {
    const map = new Map();
    for (let i = 0; i < 1000; i++) map.set(`key_${i}`, { value: i, data: `payload_${i}` });
    for (let i = 0; i < 1000; i++) map.get(`key_${i}`);
});

// ═══════════════════════════════════════════════════════════════════════
// BENCHMARK 6: Array Operations
// ═══════════════════════════════════════════════════════════════════════
const benchArray = () => runBench('Array — map/filter/reduce 10K items', 500, () => {
    const arr = Array.from({ length: 10000 }, (_, i) => i);
    void arr.map(x => x * 2).filter(x => x % 3 === 0).reduce((a, x) => a + x, 0);
});

// ═══════════════════════════════════════════════════════════════════════
// BENCHMARK 7: Error Handling (try/catch vs OMNI monadic)
// ═══════════════════════════════════════════════════════════════════════
const benchTryCatch = () => runBench('try/catch — 10K error handling', 10000, () => {
    try { const x = 42 * 2 + 10; void x.toString(); } catch (e) { /* never */ }
});

// ═══════════════════════════════════════════════════════════════════════
// BENCHMARK 8: Filesystem
// ═══════════════════════════════════════════════════════════════════════
const benchFS = () => {
    const dir = path.join(os.tmpdir(), 'node_bench');
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    return runBench('FS Read/Write — Node.js fs', 1000, () => {
        const data = 'Node.js Benchmark Data — ' + Date.now() + '\n';
        fs.writeFileSync(path.join(dir, 'test.txt'), data);
        void fs.readFileSync(path.join(dir, 'test.txt'), 'utf8');
    });
};

// ═══════════════════════════════════════════════════════════════════════
// BENCHMARK 9: UUID Generation
// ═══════════════════════════════════════════════════════════════════════
const benchUUID = () => runBench('UUID v4 Generation — Node.js crypto', 50000, () => {
    void crypto.randomUUID();
});

// ═══════════════════════════════════════════════════════════════════════
// BENCHMARK 10: Encrypt/Decrypt
// ═══════════════════════════════════════════════════════════════════════
const benchEncrypt = () => {
    const key = Buffer.from('omni-secret-key-256bit-prod-key!'); // exactly 32 bytes
    return runBench('Encrypt+Decrypt — AES-256 Cycle', 5000, () => {
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
        let encrypted = cipher.update('Sensitive financial data: $1,000,000.00', 'utf8', 'hex');
        encrypted += cipher.final('hex');
        const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
        let decrypted = decipher.update(encrypted, 'hex', 'utf8');
        decrypted += decipher.final('utf8');
    });
};

// ═══════════════════════════════════════════════════════════════════════
// 🏁 MAIN
// ═══════════════════════════════════════════════════════════════════════
console.log('');
console.log(bold(yellow('  ╔══════════════════════════════════════════════════════════╗')));
console.log(bold(yellow('  ║       🐌 NODE.JS BENCHMARK — For Comparison            ║')));
console.log(bold(yellow('  ║            Running Same Tests as OMNI                   ║')));
console.log(bold(yellow('  ╚══════════════════════════════════════════════════════════╝')));
console.log('');
console.log(dim(`  Runtime: Node.js ${process.version}`));
console.log(dim(`  Platform: ${os.platform()} / ${os.arch()}`));
console.log(dim(`  CWD: ${process.cwd()}`));
console.log('');
console.log(bold('  ─────────────────────────────────────────────────────────'));
console.log(bold('  BENCHMARK                           OPS/SEC    TIME     '));
console.log(bold('  ─────────────────────────────────────────────────────────'));

const benchmarks = [benchFibonacci, benchString, benchJSON, benchCrypto, benchMap, benchArray, benchTryCatch, benchFS, benchUUID, benchEncrypt];
let totalOps = 0, totalTime = 0;

for (const benchFn of benchmarks) {
    const r = benchFn();
    const icon = r.ops_per_sec > 100000 ? green('🚀') : r.ops_per_sec > 10000 ? yellow('⚡') : cyan('✦');
    console.log(`  ${icon} ${r.name}`);
    console.log(`    ${bold(green(formatNumber(r.ops_per_sec) + ' ops/s'))}  ${dim(r.duration_ms.toFixed(1) + 'ms')}  ${dim('(' + r.iterations + ' iters)')}`);
    console.log('');
    totalOps += r.ops_per_sec;
    totalTime += r.duration_ms;
}

console.log(bold('  ─────────────────────────────────────────────────────────'));
console.log(bold(yellow(`  📊 TOTAL: ${formatNumber(totalOps)} combined ops/sec`)));
console.log(bold(yellow(`  ⏱️  TIME:  ${totalTime.toFixed(1)}ms total runtime`)));
console.log('');
console.log(bold(red('  ╔══════════════════════════════════════════════════════════╗')));
console.log(bold(red('  ║  ❌ NODE.JS LIMITATIONS:                                ║')));
console.log(bold(red('  ║                                                        ║')));
console.log(bold(red('  ║  ❌ 100MB+ install size (vs OMNI 11MB binary)           ║')));
console.log(bold(red('  ║  ❌ C++ binding overhead for every built-in module      ║')));
console.log(bold(red('  ║  ❌ try/catch exception overhead (vs monadic Results)   ║')));
console.log(bold(red('  ║  ❌ Garbage collector pauses (vs Rust ownership)        ║')));
console.log(bold(red('  ║  ❌ No built-in permissions (full system access)        ║')));
console.log(bold(red('  ║  ❌ node_modules bloat (vs omni_modules flat)           ║')));
console.log(bold(red('  ║  ❌ 60+ separate C++ bindings (vs 1 Rust syscall hub)   ║')));
console.log(bold(red('  ║                                                        ║')));
console.log(bold(red('  ║  Node.js = Legacy Architecture + Technical Debt         ║')));
console.log(bold(red('  ╚══════════════════════════════════════════════════════════╝')));
console.log('');
