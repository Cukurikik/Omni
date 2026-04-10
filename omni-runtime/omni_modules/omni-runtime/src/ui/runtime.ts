// ============================================================
// 📦 omni-runtime/ui/runtime.ts — TypeScript Bindings
// ============================================================

import { Result, Ok, Err, OmniError } from "omni-std";

declare const OmniNative: any;

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
