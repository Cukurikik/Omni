// ==========================================
// 🗺️ OMNI-LAND: NATIVE PATH BINDINGS
// ==========================================
// Wrapper untuk Go path/filepath — otomatis menyesuaikan
// separator berdasarkan OS (Windows='\', Linux='/')
//
// IMPORT: import { path } from 'omni/path';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

/**
 * Gabungkan path fragments menjadi satu path yang valid.
 * ⚡ Go filepath.Join() — auto-normalize separator
 */
export function join(...paths: string[]): string {
    const res = OmniNative.syscall("path_join", { paths });
    return res.result as string;
}

/**
 * Resolve path menjadi absolute path.
 * ⚡ Go filepath.Abs() — tidak perlu process.cwd() hacks
 */
export function resolve(...paths: string[]): string {
    const res = OmniNative.syscall("path_resolve", { paths });
    return res.result as string;
}

/**
 * Ambil ekstensi file (termasuk dot).
 * Contoh: extname("video.mp4") → ".mp4"
 */
export function extname(filename: string): string {
    const res = OmniNative.syscall("path_ext", { filename });
    return res.result as string;
}

/**
 * Ambil nama file dari path (tanpa direktori).
 * Contoh: basename("/usr/bin/omni") → "omni"
 */
export function basename(filepath: string, ext?: string): string {
    const res = OmniNative.syscall("path_basename", { filepath, ext: ext || "" });
    return res.result as string;
}

/**
 * Ambil direktori parent dari path.
 * Contoh: dirname("/usr/bin/omni") → "/usr/bin"
 */
export function dirname(filepath: string): string {
    const res = OmniNative.syscall("path_dirname", { filepath });
    return res.result as string;
}

/**
 * Normalize path (hapus ./ dan ../)
 */
export function normalize(filepath: string): string {
    const res = OmniNative.syscall("path_normalize", { filepath });
    return res.result as string;
}

/**
 * Cek apakah path adalah absolute.
 */
export function isAbsolute(filepath: string): boolean {
    const res = OmniNative.syscall("path_is_absolute", { filepath });
    return res.result as boolean;
}

/**
 * Hitung relative path dari 'from' ke 'to'.
 */
export function relative(from: string, to: string): string {
    const res = OmniNative.syscall("path_relative", { from, to });
    return res.result as string;
}

/**
 * Parse path menjadi komponen { root, dir, base, ext, name }.
 */
export function parse(filepath: string): {
    root: string;
    dir: string;
    base: string;
    ext: string;
    name: string;
} {
    const res = OmniNative.syscall("path_parse", { filepath });
    return res.result as { root: string; dir: string; base: string; ext: string; name: string };
}

/**
 * Platform separator ('\\' di Windows, '/' di Linux/Mac)
 */
export function sep(): string {
    const res = OmniNative.syscall("path_sep", {});
    return res.result as string;
}

/**
 * Platform delimiter (';' di Windows, ':' di Linux/Mac)
 */
export function delimiter(): string {
    const res = OmniNative.syscall("path_delimiter", {});
    return res.result as string;
}

export const path = {
    join,
    resolve,
    extname,
    basename,
    dirname,
    normalize,
    isAbsolute,
    relative,
    parse,
    sep,
    delimiter,
};

export default path;
