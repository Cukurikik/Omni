// ==========================================
// ⚙️ OMNI-LAND: NATIVE PROCESS CONTROL
// ==========================================
// Node.js process global — reimplemented via Go os + runtime.
//
// IMPORT: import { process } from 'omni/process';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

/**
 * Keluar dari proses dengan exit code.
 */
export function exit(code?: number): never {
    OmniNative.syscall("process_exit", { code: code ?? 0 });
    throw new Error("Process exited"); // Should never reach here
}

/**
 * Current Working Directory.
 */
export function cwd(): string {
    return OmniNative.syscall("process_cwd", {}).result as string;
}

/**
 * Ubah working directory.
 */
export function chdir(dir: string): void {
    const res = OmniNative.syscall("process_chdir", { dir });
    if (res.error) throw new Error(`[OMNI-PROCESS] ${res.error}`);
}

/**
 * Command-line arguments (argv).
 */
export function argv(): string[] {
    return OmniNative.syscall("process_argv", {}).result as string[];
}

/**
 * Process ID.
 */
export function pid(): number {
    return OmniNative.syscall("os_pid", {}).result as number;
}

/**
 * Parent Process ID.
 */
export function ppid(): number {
    return OmniNative.syscall("process_ppid", {}).result as number;
}

/**
 * Executable path (omni.exe).
 */
export function execPath(): string {
    return OmniNative.syscall("process_exec_path", {}).result as string;
}

/**
 * Environment variables sebagai Record.
 */
export function env(): Record<string, string> {
    return OmniNative.syscall("os_env", {}).result as Record<string, string>;
}

/**
 * Ambil satu environment variable.
 */
export function getenv(key: string): string | undefined {
    const res = OmniNative.syscall("os_getenv", { key });
    return res.result as string | undefined;
}

/**
 * Set environment variable.
 */
export function setenv(key: string, value: string): void {
    OmniNative.syscall("process_setenv", { key, value });
}

/**
 * Memory usage saat ini.
 */
export function memoryUsage(): {
    heapUsed: number;
    heapTotal: number;
    rss: number;
    goroutines: number;
} {
    return OmniNative.syscall("process_memory", {}).result as any;
}

/**
 * Uptime proses dalam detik.
 */
export function uptime(): number {
    return OmniNative.syscall("process_uptime", {}).result as number;
}

/**
 * OMNI Runtime version.
 */
export function version(): string {
    return OmniNative.syscall("process_version", {}).result as string;
}

/**
 * Platform info.
 */
export function platform(): string {
    return OmniNative.syscall("os_platform", {}).result as string;
}

/**
 * High-resolution time (nanosecond precision).
 */
export function hrtime(): [number, number] {
    const res = OmniNative.syscall("timer_hrtime", {});
    const ns = Number(res.result);
    return [Math.floor(ns / 1e9), ns % 1e9];
}

export const process = {
    exit,
    cwd,
    chdir,
    argv,
    pid,
    ppid,
    execPath,
    env,
    getenv,
    setenv,
    memoryUsage,
    uptime,
    version,
    platform,
    hrtime,
};

export default process;
