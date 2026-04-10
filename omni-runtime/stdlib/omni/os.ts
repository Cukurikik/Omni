// ==========================================
// 🖥️ OMNI-LAND: NATIVE OS TELEMETRY
// ==========================================
// Membaca data OS langsung dari Golang runtime — tanpa
// overhead parsing /proc/cpuinfo seperti Node.js
//
// IMPORT: import { os } from 'omni/os';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

/**
 * Arsitektur CPU: "amd64", "arm64", "386"
 * ⚡ Langsung dari runtime.GOARCH
 */
export function arch(): string {
    return OmniNative.syscall("os_arch", {}).result as string;
}

/**
 * Platform OS: "windows", "linux", "darwin"
 * ⚡ Langsung dari runtime.GOOS
 */
export function platform(): string {
    return OmniNative.syscall("os_platform", {}).result as string;
}

/**
 * Jumlah Core CPU logis (termasuk HyperThread)
 * ⚡ Langsung dari runtime.NumCPU()
 */
export function cpus(): number {
    return OmniNative.syscall("os_cpus", {}).result as number;
}

/**
 * Total RAM fisik dalam byte
 */
export function totalmem(): number {
    return OmniNative.syscall("os_totalmem", {}).result as number;
}

/**
 * Sisa RAM yang tersedia dalam byte
 * ⚡ Native syscall — bukan estimasi VM
 */
export function freemem(): number {
    return OmniNative.syscall("os_freemem", {}).result as number;
}

/**
 * Hostname mesin
 */
export function hostname(): string {
    return OmniNative.syscall("os_hostname", {}).result as string;
}

/**
 * Home directory user saat ini
 */
export function homedir(): string {
    return OmniNative.syscall("os_homedir", {}).result as string;
}

/**
 * Temporary directory system
 */
export function tmpdir(): string {
    return OmniNative.syscall("os_tmpdir", {}).result as string;
}

/**
 * Uptime OS dalam detik
 */
export function uptime(): number {
    return OmniNative.syscall("os_uptime", {}).result as number;
}

/**
 * End-of-line character: "\r\n" (Windows) atau "\n" (Linux/Mac)
 */
export function eol(): string {
    return OmniNative.syscall("os_eol", {}).result as string;
}

/**
 * Environment variables sebagai Record
 */
export function env(): Record<string, string> {
    return OmniNative.syscall("os_env", {}).result as Record<string, string>;
}

/**
 * Ambil satu environment variable
 */
export function getenv(key: string): string | undefined {
    const res = OmniNative.syscall("os_getenv", { key });
    return res.result as string | undefined;
}

/**
 * Process ID (PID) saat ini
 */
export function pid(): number {
    return OmniNative.syscall("os_pid", {}).result as number;
}

/**
 * Informasi lengkap OS
 */
export function info(): {
    arch: string;
    platform: string;
    hostname: string;
    cpus: number;
    totalmem: number;
    freemem: number;
    uptime: number;
} {
    return OmniNative.syscall("os_info", {}).result as any;
}

export const os = {
    arch,
    platform,
    cpus,
    totalmem,
    freemem,
    hostname,
    homedir,
    tmpdir,
    uptime,
    eol,
    env,
    getenv,
    pid,
    info,
};

export default os;
