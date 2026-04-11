// ============================================================
// omni-runtime/ui/runtime.ts — TypeScript Bindings
// ============================================================

// Result/Error types (self-contained — no external dependency)
export interface OmniError {
    code: string;
    message: string;
}

export type Result<T, E> =
    | { ok: true; value: T }
    | { ok: false; error: E };

export function Ok<T>(value: T): Result<T, never> {
    return { ok: true, value };
}

export function Err<E>(error: E): Result<never, E> {
    return { ok: false, error };
}

// Native bridge declaration
declare const OmniNative: {
    syscall(name: string, args: Record<string, unknown>): any;
};

export class EventLoop {
    static nextTick(callback: () => void): void {
        OmniNative.syscall("runtime_next_tick", { handler: callback });
    }

    static setTimeout(callback: () => void, ms: number): number {
        return OmniNative.syscall("runtime_set_timeout", { handler: callback, delay: ms });
    }

    static setInterval(callback: () => void, ms: number): number {
        return OmniNative.syscall("runtime_set_interval", { handler: callback, delay: ms });
    }

    static clearTimer(id: number): void {
        OmniNative.syscall("runtime_clear_timer", { id });
    }
}

export function spawn(task: () => void): Result<number, OmniError> {
    const result = OmniNative.syscall("runtime_spawn", { task });
    if (result.error) {
        return Err({ code: "E201", message: result.error });
    }
    return Ok(result.taskId as number);
}

export function sleep(ms: number): void {
    OmniNative.syscall("runtime_sleep", { delay: ms });
}

export function exit(code: number = 0): never {
    OmniNative.syscall("runtime_exit", { code });
    throw new Error("unreachable");
}

export function uptime(): Result<number, OmniError> {
    const result = OmniNative.syscall("runtime_uptime", {});
    if (result.error) {
        return Err({ code: "E203", message: "Failed to get uptime" });
    }
    return Ok(result.uptime as number);
}

export function version(): string {
    return "omni-runtime v2.0.0";
}
