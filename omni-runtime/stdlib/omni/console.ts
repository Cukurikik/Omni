// ==========================================
// 📋 OMNI-LAND: NATIVE CONSOLE MODULE
// ==========================================
// Enhanced console yang meneruskan output ke Go logger.
//
// IMPORT: import { console } from 'omni/console';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

const _timers: Map<string, number> = new Map();
let _groupDepth = 0;

function _prefix(): string {
    return "  ".repeat(_groupDepth);
}

/**
 * Log ke stdout (via Go log.Println).
 */
export function log(...args: any[]): void {
    const msg = args.map(a => typeof a === "object" ? JSON.stringify(a, null, 2) : String(a)).join(" ");
    OmniNative.syscall("console_log", { level: "info", message: _prefix() + msg });
}

/**
 * Log warning.
 */
export function warn(...args: any[]): void {
    const msg = args.map(a => typeof a === "object" ? JSON.stringify(a) : String(a)).join(" ");
    OmniNative.syscall("console_log", { level: "warn", message: "⚠️ " + _prefix() + msg });
}

/**
 * Log error.
 */
export function error(...args: any[]): void {
    const msg = args.map(a => typeof a === "object" ? JSON.stringify(a) : String(a)).join(" ");
    OmniNative.syscall("console_log", { level: "error", message: "❌ " + _prefix() + msg });
}

/**
 * Log debug (hanya tampil jika DEBUG=true).
 */
export function debug(...args: any[]): void {
    const msg = args.map(a => typeof a === "object" ? JSON.stringify(a) : String(a)).join(" ");
    OmniNative.syscall("console_log", { level: "debug", message: "🔍 " + _prefix() + msg });
}

/**
 * Log tabel data (array of objects).
 */
export function table(data: any[]): void {
    if (!Array.isArray(data) || data.length === 0) {
        log(data);
        return;
    }
    const keys = Object.keys(data[0]);
    const header = keys.join("\t| ");
    const separator = keys.map(k => "-".repeat(k.length)).join("-+-");
    const rows = data.map(row => keys.map(k => String(row[k] ?? "")).join("\t| ")).join("\n");
    log(`\n${header}\n${separator}\n${rows}`);
}

/**
 * Mulai timer (untuk mengukur durasi).
 */
export function time(label: string): void {
    _timers.set(label, Date.now());
}

/**
 * Akhiri timer dan tampilkan durasi.
 */
export function timeEnd(label: string): void {
    const start = _timers.get(label);
    if (start) {
        log(`${label}: ${Date.now() - start}ms`);
        _timers.delete(label);
    }
}

/**
 * Log durasi tanpa menghentikan timer.
 */
export function timeLog(label: string, ...args: any[]): void {
    const start = _timers.get(label);
    if (start) {
        const msg = args.length > 0 ? " " + args.join(" ") : "";
        log(`${label}: ${Date.now() - start}ms${msg}`);
    }
}

/**
 * Increment counter.
 */
const _counters: Map<string, number> = new Map();
export function count(label?: string): void {
    const l = label ?? "default";
    const c = (_counters.get(l) ?? 0) + 1;
    _counters.set(l, c);
    log(`${l}: ${c}`);
}

export function countReset(label?: string): void {
    _counters.set(label ?? "default", 0);
}

/**
 * Assert — log error jika condition false.
 */
export function assert(condition: any, ...args: any[]): void {
    if (!condition) {
        error("Assertion failed:", ...args);
    }
}

/**
 * Group log output (indent).
 */
export function group(label?: string): void {
    if (label) log(label);
    _groupDepth++;
}

export function groupEnd(): void {
    if (_groupDepth > 0) _groupDepth--;
}

/**
 * Clear console.
 */
export function clear(): void {
    OmniNative.syscall("console_clear", {});
}

export const console = {
    log, warn, error, debug,
    table, time, timeEnd, timeLog,
    count, countReset, assert,
    group, groupEnd, clear,
};

export default console;
