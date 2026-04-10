// ==========================================
// 🔧 OMNI-LAND: NATIVE UTIL MODULE
// ==========================================
// Utilitas umum Node.js — reimplemented.
//
// IMPORT: import { util } from 'omni/util';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

/**
 * Inspeksi objek menjadi string yang readable (untuk debugging).
 */
export function inspect(obj: any, options?: { depth?: number; colors?: boolean }): string {
    const depth = options?.depth ?? 3;
    return _deepInspect(obj, 0, depth);
}

function _deepInspect(obj: any, level: number, maxDepth: number): string {
    if (level > maxDepth) return "[Object]";
    if (obj === null) return "null";
    if (obj === undefined) return "undefined";
    if (typeof obj === "string") return `'${obj}'`;
    if (typeof obj === "number" || typeof obj === "boolean") return String(obj);
    if (typeof obj === "function") return `[Function: ${obj.name || "anonymous"}]`;
    if (Array.isArray(obj)) {
        const items = obj.map(item => _deepInspect(item, level + 1, maxDepth));
        return `[ ${items.join(", ")} ]`;
    }
    if (typeof obj === "object") {
        const indent = "  ".repeat(level + 1);
        const entries = Object.entries(obj).map(([k, v]) =>
            `${indent}${k}: ${_deepInspect(v, level + 1, maxDepth)}`
        );
        return `{\n${entries.join(",\n")}\n${"  ".repeat(level)}}`;
    }
    return String(obj);
}

/**
 * Format string seperti printf.
 * Supports: %s (string), %d (number), %j (JSON), %% (literal %)
 */
export function format(fmt: string, ...args: any[]): string {
    let i = 0;
    return fmt.replace(/%[sdj%]/g, (match) => {
        if (match === "%%") return "%";
        if (i >= args.length) return match;
        const arg = args[i++];
        switch (match) {
            case "%s": return String(arg);
            case "%d": return Number(arg).toString();
            case "%j":
                try { return JSON.stringify(arg); }
                catch { return "[Circular]"; }
            default: return match;
        }
    });
}

/**
 * Cek apakah value adalah tipe tertentu.
 */
export function isArray(value: any): value is Array<any> { return Array.isArray(value); }
export function isString(value: any): value is string { return typeof value === "string"; }
export function isNumber(value: any): value is number { return typeof value === "number" && !isNaN(value); }
export function isBoolean(value: any): value is boolean { return typeof value === "boolean"; }
export function isObject(value: any): value is object { return value !== null && typeof value === "object" && !Array.isArray(value); }
export function isFunction(value: any): value is Function { return typeof value === "function"; }
export function isNull(value: any): value is null { return value === null; }
export function isUndefined(value: any): value is undefined { return value === undefined; }
export function isNullOrUndefined(value: any): value is null | undefined { return value == null; }
export function isRegExp(value: any): value is RegExp { return value instanceof RegExp; }
export function isDate(value: any): value is Date { return value instanceof Date; }
export function isError(value: any): value is Error { return value instanceof Error; }

/**
 * Promisify-style wrapper (untuk kompatibilitas pola callback).
 */
export function callbackify<T>(fn: () => T): (callback: (err: Error | null, result?: T) => void) => void {
    return (callback) => {
        try {
            const result = fn();
            callback(null, result);
        } catch (e: any) {
            callback(e);
        }
    };
}

/**
 * Deep clone object (menggunakan JSON round-trip).
 */
export function deepClone<T>(obj: T): T {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Deep merge objects.
 */
export function deepMerge<T extends Record<string, any>>(target: T, ...sources: Partial<T>[]): T {
    for (const source of sources) {
        for (const key of Object.keys(source)) {
            const sv = (source as any)[key];
            const tv = (target as any)[key];
            if (isObject(sv) && isObject(tv)) {
                (target as any)[key] = deepMerge({ ...tv }, sv);
            } else {
                (target as any)[key] = sv;
            }
        }
    }
    return target;
}

/**
 * Debounce function.
 */
export function debounce(fn: (...args: any[]) => void, delayMs: number): (...args: any[]) => void {
    let timer: any = null;
    return (...args: any[]) => {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delayMs);
    };
}

/**
 * Throttle function.
 */
export function throttle(fn: (...args: any[]) => void, intervalMs: number): (...args: any[]) => void {
    let lastCall = 0;
    return (...args: any[]) => {
        const now = Date.now();
        if (now - lastCall >= intervalMs) {
            lastCall = now;
            fn(...args);
        }
    };
}

export const util = {
    inspect,
    format,
    isArray, isString, isNumber, isBoolean, isObject, isFunction,
    isNull, isUndefined, isNullOrUndefined, isRegExp, isDate, isError,
    callbackify,
    deepClone,
    deepMerge,
    debounce,
    throttle,
};

export default util;
