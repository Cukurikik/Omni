// ==========================================
// 📦 OMNI-LAND: NATIVE COMPRESSION (ZLIB/GZIP)
// ==========================================
// Go compress/gzip + compress/zlib — native compression.
//
// IMPORT: import { zlib } from 'omni/zlib';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

/**
 * Compress data menggunakan Gzip.
 * @param data - String data mentah
 * @param level - Compression level 1-9 (default 6)
 * @returns Base64-encoded compressed data
 */
export function gzip(data: string, level?: number): string {
    const res = OmniNative.syscall("zlib_gzip", { data, level: level ?? 6 });
    if (res.error) throw new Error(`[OMNI-ZLIB] ${res.error}`);
    return res.result as string;
}

/**
 * Decompress data dari Gzip.
 */
export function gunzip(compressedBase64: string): string {
    const res = OmniNative.syscall("zlib_gunzip", { data: compressedBase64 });
    if (res.error) throw new Error(`[OMNI-ZLIB] ${res.error}`);
    return res.result as string;
}

/**
 * Compress data menggunakan Deflate (raw zlib).
 */
export function deflate(data: string, level?: number): string {
    const res = OmniNative.syscall("zlib_deflate", { data, level: level ?? 6 });
    if (res.error) throw new Error(`[OMNI-ZLIB] ${res.error}`);
    return res.result as string;
}

/**
 * Decompress data dari Deflate.
 */
export function inflate(compressedBase64: string): string {
    const res = OmniNative.syscall("zlib_inflate", { data: compressedBase64 });
    if (res.error) throw new Error(`[OMNI-ZLIB] ${res.error}`);
    return res.result as string;
}

/**
 * Compress file secara streaming (untuk file besar).
 */
export function gzipFile(inputPath: string, outputPath: string, level?: number): void {
    const res = OmniNative.syscall("zlib_gzip_file", { inputPath, outputPath, level: level ?? 6 });
    if (res.error) throw new Error(`[OMNI-ZLIB] ${res.error}`);
}

/**
 * Decompress file secara streaming.
 */
export function gunzipFile(inputPath: string, outputPath: string): void {
    const res = OmniNative.syscall("zlib_gunzip_file", { inputPath, outputPath });
    if (res.error) throw new Error(`[OMNI-ZLIB] ${res.error}`);
}

export const zlib = {
    gzip,
    gunzip,
    deflate,
    inflate,
    gzipFile,
    gunzipFile,
};

export default zlib;
