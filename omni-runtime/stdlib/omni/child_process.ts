// ==========================================
// 🚀 OMNI-LAND: NATIVE CHILD PROCESS
// ==========================================
// Node.js child_process.exec  → libuv thread pool
// OMNI execSync/spawn → Go os/exec.Command + Goroutine
//
// IMPORT: import { exec, execSync, spawn } from 'omni/child_process';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
    registerCallback: (id: string, fn: Function) => void;
};

export interface ExecResult {
    stdout: string;
    stderr: string;
    exitCode: number;
}

export interface SpawnOptions {
    cwd?: string;
    env?: Record<string, string>;
    timeout?: number;     // milliseconds, 0 = no timeout
    shell?: boolean;      // wrap in system shell
}

/**
 * Eksekusi perintah secara sinkron dan tunggu hasilnya.
 * ⚡ Go exec.Command().CombinedOutput()
 */
export function execSync(command: string, options?: SpawnOptions): ExecResult {
    const res = OmniNative.syscall("child_exec_sync", {
        command,
        cwd: options?.cwd ?? "",
        env: options?.env ?? {},
        timeout: options?.timeout ?? 0,
        shell: options?.shell ?? true,
    });
    if (res.error) throw new Error(`[OMNI-EXEC] ${res.error}`);
    return res.result as ExecResult;
}

/**
 * Eksekusi perintah secara asinkron (dalam Goroutine terpisah).
 * Callback dipanggil saat selesai.
 */
export function exec(
    command: string,
    options: SpawnOptions | undefined,
    callback: (err: Error | null, result: ExecResult) => void,
): string {
    const callbackId = `exec_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    OmniNative.registerCallback(callbackId, (data: any) => {
        if (data.error) {
            callback(new Error(data.error), { stdout: "", stderr: data.error, exitCode: -1 });
        } else {
            callback(null, data as ExecResult);
        }
    });

    const res = OmniNative.syscall("child_exec_async", {
        command,
        callbackId,
        cwd: options?.cwd ?? "",
        env: options?.env ?? {},
        timeout: options?.timeout ?? 0,
        shell: options?.shell ?? true,
    });
    return res.processId as string;
}

/**
 * Spawn proses dan stream stdout/stderr secara real-time.
 * @returns processId untuk monitoring/kill
 */
export function spawn(
    command: string,
    args: string[],
    options?: SpawnOptions & {
        onStdout?: (data: string) => void;
        onStderr?: (data: string) => void;
        onExit?: (code: number) => void;
    },
): string {
    const processId = `spawn_${Date.now()}`;
    
    if (options?.onStdout) {
        OmniNative.registerCallback(`${processId}_stdout`, options.onStdout);
    }
    if (options?.onStderr) {
        OmniNative.registerCallback(`${processId}_stderr`, options.onStderr);
    }
    if (options?.onExit) {
        OmniNative.registerCallback(`${processId}_exit`, options.onExit);
    }

    const res = OmniNative.syscall("child_spawn", {
        command,
        args,
        processId,
        cwd: options?.cwd ?? "",
        env: options?.env ?? {},
        timeout: options?.timeout ?? 0,
    });
    if (res.error) throw new Error(`[OMNI-SPAWN] ${res.error}`);
    return res.processId as string;
}

/**
 * Kill spawned process.
 */
export function kill(processId: string, signal?: string): void {
    OmniNative.syscall("child_kill", { processId, signal: signal ?? "SIGTERM" });
}

export const child_process = {
    execSync,
    exec,
    spawn,
    kill,
};

export default child_process;
