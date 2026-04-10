// ==========================================
// ⏱️ OMNI-LAND: NATIVE TIMERS & SCHEDULING
// ==========================================
// Node.js timers berjalan di libuv event loop.
// OMNI timers dikelola oleh Goroutines + time.Sleep native.
//
// IMPORT: import { setTimeout, setInterval } from 'omni/timers';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
    registerCallback: (id: string, fn: Function) => void;
};

/**
 * Jalankan fungsi setelah delay (ms).
 * ⚡ Dikelola otomatis oleh time.AfterFunc() Golang
 * @returns timerId yang bisa digunakan untuk clearTimeout
 */
export function setTimeout(callback: () => void, delayMs: number): string {
    const callbackId = `timer_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    OmniNative.registerCallback(callbackId, callback);
    const res = OmniNative.syscall("timer_set_timeout", {
        callbackId,
        delayMs,
    });
    return res.timerId as string;
}

/**
 * Batalkan timer yang dijadwalkan.
 */
export function clearTimeout(timerId: string): void {
    OmniNative.syscall("timer_clear", { timerId });
}

/**
 * Jalankan fungsi berulang setiap interval (ms).
 * ⚡ Goroutine sendiri — tidak block main thread.
 * @returns intervalId yang bisa digunakan untuk clearInterval
 */
export function setInterval(callback: () => void, intervalMs: number): string {
    const callbackId = `interval_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    OmniNative.registerCallback(callbackId, callback);
    const res = OmniNative.syscall("timer_set_interval", {
        callbackId,
        intervalMs,
    });
    return res.intervalId as string;
}

/**
 * Batalkan interval yang berjalan.
 */
export function clearInterval(intervalId: string): void {
    OmniNative.syscall("timer_clear", { timerId: intervalId });
}

/**
 * Sleep — block eksekusi selama durasi tertentu.
 * ⚡ Go time.Sleep() — true sleep, bukan busy-wait.
 */
export function sleep(ms: number): void {
    OmniNative.syscall("timer_sleep", { ms });
}

/**
 * High-resolution timer (nanosecond precision).
 * ⚡ Go time.Now().UnixNano()
 */
export function hrtime(): bigint {
    const res = OmniNative.syscall("timer_hrtime", {});
    return BigInt(res.result as string);
}

export const timers = {
    setTimeout,
    clearTimeout,
    setInterval,
    clearInterval,
    sleep,
    hrtime,
};

export default timers;
