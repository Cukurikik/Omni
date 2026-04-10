// ==========================================
// 🔄 OMNI-LAND: NATIVE STREAM PROCESSING
// ==========================================
// Node.js Streams berjalan di JavaScript heap.
// OMNI Streams menggunakan Go io.Reader/io.Writer + Goroutine pipelines.
//
// IMPORT: import { createReadStream, createWriteStream, pipeline } from 'omni/stream';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
    registerCallback: (id: string, fn: Function) => void;
};

/**
 * Buka file untuk streaming read.
 * ⚡ Go io.Reader — buffer 64KB, data mengalir tanpa load seluruh file.
 * @returns streamId yang bisa digunakan dengan onData/onEnd
 */
export function createReadStream(filePath: string, options?: {
    bufferSize?: number;     // Default 65536 (64KB)
    start?: number;          // Start offset in bytes
    end?: number;            // End offset in bytes
    encoding?: string;       // "utf8" | "binary"
}): string {
    const res = OmniNative.syscall("stream_read_open", {
        filePath,
        bufferSize: options?.bufferSize ?? 65536,
        start: options?.start ?? 0,
        end: options?.end ?? -1,
        encoding: options?.encoding ?? "utf8",
    });
    if (res.error) throw new Error(`[OMNI-STREAM] ${res.error}`);
    return res.streamId as string;
}

/**
 * Buka file untuk streaming write.
 * ⚡ Go bufio.Writer — auto-flush di background.
 */
export function createWriteStream(filePath: string, options?: {
    append?: boolean;
    bufferSize?: number;
}): string {
    const res = OmniNative.syscall("stream_write_open", {
        filePath,
        append: options?.append ?? false,
        bufferSize: options?.bufferSize ?? 65536,
    });
    if (res.error) throw new Error(`[OMNI-STREAM] ${res.error}`);
    return res.streamId as string;
}

/**
 * Tulis data ke write stream.
 */
export function streamWrite(streamId: string, data: string): void {
    const res = OmniNative.syscall("stream_write", { streamId, data });
    if (res.error) throw new Error(`[OMNI-STREAM] ${res.error}`);
}

/**
 * Tutup stream dan flush buffer.
 */
export function streamClose(streamId: string): void {
    OmniNative.syscall("stream_close", { streamId });
}

/**
 * Daftarkan callback untuk data yang masuk pada read stream.
 */
export function onData(streamId: string, callback: (chunk: string) => void): void {
    const callbackId = `stream_data_${streamId}`;
    OmniNative.registerCallback(callbackId, callback);
    OmniNative.syscall("stream_on_data", { streamId, callbackId });
}

/**
 * Daftarkan callback untuk stream selesai.
 */
export function onEnd(streamId: string, callback: () => void): void {
    const callbackId = `stream_end_${streamId}`;
    OmniNative.registerCallback(callbackId, callback);
    OmniNative.syscall("stream_on_end", { streamId, callbackId });
}

/**
 * Daftarkan callback untuk error pada stream.
 */
export function onError(streamId: string, callback: (err: string) => void): void {
    const callbackId = `stream_error_${streamId}`;
    OmniNative.registerCallback(callbackId, callback);
    OmniNative.syscall("stream_on_error", { streamId, callbackId });
}

/**
 * Pipeline — sambungkan read stream ke write stream.
 * ⚡ Go io.Copy() — zero-copy transfer menggunakan sendfile() syscall!
 */
export function pipeline(readStreamId: string, writeStreamId: string): void {
    const res = OmniNative.syscall("stream_pipeline", {
        readStreamId,
        writeStreamId,
    });
    if (res.error) throw new Error(`[OMNI-STREAM] Pipeline gagal: ${res.error}`);
}

/**
 * Copy file menggunakan streaming pipeline (efisien untuk file besar).
 */
export function copyFile(src: string, dest: string): void {
    const res = OmniNative.syscall("stream_copy_file", { src, dest });
    if (res.error) throw new Error(`[OMNI-STREAM] Copy gagal: ${res.error}`);
}

export const stream = {
    createReadStream,
    createWriteStream,
    streamWrite,
    streamClose,
    onData,
    onEnd,
    onError,
    pipeline,
    copyFile,
};

export default stream;
