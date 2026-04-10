// ==========================================
// ⚛️ OMNI-LAND: NATIVE FILE SYSTEM BINDINGS
// ==========================================
// Terlihat seperti JavaScript biasa, tapi di balik layar ini
// memanggil os.ReadFile Golang / std::fs Rust yang kecepatannya
// memotong overhead C++ Node.js!
//
// IMPORT: import { readFileSync, writeFileSync } from 'omni/fs';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

/**
 * Membaca file dari SSD secara sinkron.
 * ⚡ SPEK DEWA: Golang Bare-Metal I/O, bukan Node.js libuv!
 */
export function readFileSync(filePath: string): string {
    const response = OmniNative.syscall("fs_read", { path: filePath });
    if (response.error) {
        throw new Error(`[OMNI-FS] Gagal membaca file: ${response.error}`);
    }
    return response.data as string;
}

/**
 * Menulis data ke file secara sinkron.
 * ⚡ Menggunakan OMNI-BUFFER Golang untuk tulis masif ke SSD.
 */
export function writeFileSync(filePath: string, content: string): void {
    const response = OmniNative.syscall("fs_write", { path: filePath, data: content });
    if (response.error) {
        throw new Error(`[OMNI-FS] Gagal menulis file: ${response.error}`);
    }
}

/**
 * Cek apakah file/folder ada di filesystem.
 */
export function existsSync(filePath: string): boolean {
    const response = OmniNative.syscall("fs_exists", { path: filePath });
    return response.exists === true;
}

/**
 * Buat direktori (opsional rekursif seperti mkdir -p).
 */
export function mkdirSync(dirPath: string, options?: { recursive?: boolean }): void {
    const response = OmniNative.syscall("fs_mkdir", { 
        path: dirPath, 
        recursive: options?.recursive ?? false 
    });
    if (response.error) {
        throw new Error(`[OMNI-FS] Gagal membuat direktori: ${response.error}`);
    }
}

/**
 * Baca isi direktori — daftar file dan subfolder.
 */
export function readdirSync(dirPath: string): Array<{ name: string; isDir: boolean }> {
    const response = OmniNative.syscall("fs_readdir", { path: dirPath });
    if (response.error) {
        throw new Error(`[OMNI-FS] Gagal membaca direktori: ${response.error}`);
    }
    return response.entries as Array<{ name: string; isDir: boolean }>;
}

/**
 * Hapus file atau direktori.
 */
export function removeSync(filePath: string): void {
    const response = OmniNative.syscall("fs_remove", { path: filePath });
    if (response.error) {
        throw new Error(`[OMNI-FS] Gagal menghapus: ${response.error}`);
    }
}

/**
 * Ambil metadata file (ukuran, tipe, read-only status).
 */
export function statSync(filePath: string): {
    size: number;
    isDir: boolean;
    isFile: boolean;
    readonly: boolean;
} {
    const response = OmniNative.syscall("fs_stat", { path: filePath });
    if (response.error) {
        throw new Error(`[OMNI-FS] Gagal mengambil stat: ${response.error}`);
    }
    return response.stat as { size: number; isDir: boolean; isFile: boolean; readonly: boolean };
}

export default {
    readFileSync,
    writeFileSync,
    existsSync,
    mkdirSync,
    readdirSync,
    removeSync,
    statSync,
};
