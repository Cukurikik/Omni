// ==========================================
// 🧱 OMNI-LAND: NATIVE BUFFER OPERATIONS
// ==========================================
// Node.js Buffer ada di V8 heap. OMNI Buffer diproses oleh
// Go byte slices — operasi encoding/decoding oleh Go stdlib.
//
// IMPORT: import { buffer } from 'omni/buffer';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

/**
 * Encode string ke Base64.
 */
export function toBase64(data: string): string {
    const res = OmniNative.syscall("buffer_to_base64", { data });
    return res.result as string;
}

/**
 * Decode Base64 ke string.
 */
export function fromBase64(base64: string): string {
    const res = OmniNative.syscall("buffer_from_base64", { data: base64 });
    return res.result as string;
}

/**
 * Encode string ke Hex.
 */
export function toHex(data: string): string {
    const res = OmniNative.syscall("buffer_to_hex", { data });
    return res.result as string;
}

/**
 * Decode Hex ke string.
 */
export function fromHex(hex: string): string {
    const res = OmniNative.syscall("buffer_from_hex", { data: hex });
    return res.result as string;
}

/**
 * Hitung panjang byte dari string (UTF-8).
 */
export function byteLength(data: string, encoding?: string): number {
    const res = OmniNative.syscall("buffer_byte_length", { data, encoding: encoding ?? "utf8" });
    return res.result as number;
}

/**
 * Concat multiple string/byte arrays.
 */
export function concat(...buffers: string[]): string {
    const res = OmniNative.syscall("buffer_concat", { buffers });
    return res.result as string;
}

/**
 * Compare dua buffer (0 = equal, <0 = a < b, >0 = a > b).
 */
export function compare(a: string, b: string): number {
    const res = OmniNative.syscall("buffer_compare", { a, b });
    return res.result as number;
}

/**
 * Encode/decode antara encoding (utf8 ↔ latin1 ↔ ascii).
 */
export function transcode(data: string, from: string, to: string): string {
    const res = OmniNative.syscall("buffer_transcode", { data, from, to });
    if (res.error) throw new Error(`[OMNI-BUFFER] ${res.error}`);
    return res.result as string;
}

export const buffer = {
    toBase64,
    fromBase64,
    toHex,
    fromHex,
    byteLength,
    concat,
    compare,
    transcode,
};

export default buffer;
