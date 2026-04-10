#!/usr/bin/env node
// =====================================================
// 🚰 OMNI-PIPELINE: ES2026 Functional Pipeline Engine
// =====================================================
// Implementasi filosofi Pipeline Operator (|>) dari ES2026.
//
// MASALAH LAMA:
//   Kode framework lain penuh tumpukan fungsi bersarang:
//   funcA(funcB(funcC(data))) — membingungkan, rawan error.
//
// SOLUSI OMNI:
//   OMNI-PIPELINE mengalirkan data seperti air sungai, berurutan
//   dari satu fungsi transformasi ke fungsi berikutnya.
//
// MENGAPA BUKAN SYNTAX |> LANGSUNG?
//   Pipeline Operator masih di TC39 Stage 2 (April 2026).
//   Belum tersedia di V8/Node.js tanpa flag eksperimental.
//   Kita menggunakan runtime pipeline() yang memberikan
//   pengalaman identik TANPA bergantung pada compiler flag.
//
// PENGGUNAAN:
//   import { pipeline, pipe, pipeAsync } from '../lib/pipeline.mjs';
//
//   // Sync pipeline
//   const result = pipeline(rawText,
//       removeComments,
//       extractRequireTools,
//       generateGoRoutes,
//       lockChecksum
//   );
//
//   // Async pipeline
//   const result = await pipeAsync(inputData,
//       fetchRemoteConfig,
//       validateSchema,
//       transformData,
//       saveToDatabase
//   );
// =====================================================

/**
 * pipeline — Mengalirkan data melalui rangkaian fungsi transformasi.
 * ES2026 Pipeline Operator polyfill: `data |> fn1 |> fn2 |> fn3`
 *
 * @param {*} initialValue — Data awal yang masuk ke pipeline
 * @param {...Function} fns — Fungsi-fungsi transformasi berurutan
 * @returns {*} — Hasil akhir setelah melewati semua fungsi
 *
 * @example
 * pipeline("hello world",
 *     str => str.toUpperCase(),
 *     str => str.replace(/ /g, '_'),
 *     str => `[${str}]`
 * );
 * // Hasil: "[HELLO_WORLD]"
 */
export function pipeline(initialValue, ...fns) {
    return fns.reduce((acc, fn) => fn(acc), initialValue);
}

/**
 * pipeAsync — Pipeline asinkron untuk operasi I/O, network, dll.
 * Setiap fungsi dalam rantai bisa sync atau async.
 *
 * @param {*} initialValue — Data awal
 * @param {...Function} fns — Fungsi transformasi (async-compatible)
 * @returns {Promise<*>} — Hasil akhir
 *
 * @example
 * const result = await pipeAsync(userId,
 *     fetchUserFromDB,
 *     enrichWithMetrics,
 *     formatResponse
 * );
 */
export async function pipeAsync(initialValue, ...fns) {
    let result = initialValue;
    for (const fn of fns) {
        result = await fn(result);
    }
    return result;
}

/**
 * pipe — Compose beberapa fungsi menjadi SATU fungsi baru (curried).
 * Berguna untuk membuat transformer yang bisa di-reuse.
 *
 * @param {...Function} fns — Fungsi-fungsi yang akan di-compose
 * @returns {Function} — Fungsi komposit
 *
 * @example
 * const sanitize = pipe(
 *     removeComments,
 *     trimWhitespace,
 *     escapeHtml
 * );
 *
 * // Gunakan berulang kali:
 * sanitize(input1);
 * sanitize(input2);
 */
export function pipe(...fns) {
    return (initialValue) => fns.reduce((acc, fn) => fn(acc), initialValue);
}

/**
 * pipeAsyncCompose — Compose beberapa fungsi async menjadi satu (curried).
 *
 * @param {...Function} fns — Fungsi async yang akan di-compose
 * @returns {Function} — Fungsi komposit async
 */
export function pipeAsyncCompose(...fns) {
    return async (initialValue) => {
        let result = initialValue;
        for (const fn of fns) {
            result = await fn(result);
        }
        return result;
    };
}

// =====================================================
// 🔧 BUILT-IN PIPELINE TRANSFORMS
// =====================================================
// Fungsi-fungsi transformasi siap pakai yang bisa dimasukkan
// ke dalam pipeline OMNI-CLI.

/**
 * Hapus baris komentar (#) dari string konfigurasi.
 */
export function removeComments(text) {
    return text
        .split('\n')
        .filter(line => !line.trim().startsWith('#'))
        .join('\n');
}

/**
 * Hapus baris kosong berlebih (lebih dari 1 baris kosong berturut-turut).
 */
export function collapseBlankLines(text) {
    return text.replace(/\n{3,}/g, '\n\n');
}

/**
 * Trim whitespace di awal dan akhir setiap baris.
 */
export function trimLines(text) {
    return text
        .split('\n')
        .map(line => line.trim())
        .join('\n');
}

/**
 * Konversi teks ke UPPERCASE (berguna untuk normalisasi key).
 */
export function toUpperKeys(text) {
    return text
        .split('\n')
        .map(line => {
            const match = line.match(/^([A-Za-z_][A-Za-z0-9_]*)\s+(.*)/);
            if (match) {
                return `${match[1].toUpperCase()} ${match[2]}`;
            }
            return line;
        })
        .join('\n');
}

/**
 * Injeksi timestamp build ke dalam string konfigurasi.
 */
export function injectBuildTimestamp(text) {
    const banner = `# OMNI BUILD TIMESTAMP: ${new Date().toISOString()}\n`;
    return banner + text;
}

/**
 * Hitung checksum SHA-256 dari string (menggunakan Node.js crypto).
 * Berguna untuk OMNI-LOCK verification.
 */
export async function computeChecksum(text) {
    try {
        const { createHash } = await import('crypto');
        const hash = createHash('sha256').update(text).digest('hex');
        return { content: text, checksum: hash };
    } catch {
        // Fallback tanpa crypto (browser context)
        return { content: text, checksum: 'NO_CRYPTO_AVAILABLE' };
    }
}

// =====================================================
// ⚡ OMNI-CLI PIPELINE PRESETS
// =====================================================
// Pipeline yang sudah di-compose untuk penggunaan umum di CLI.

/**
 * sanitizeConfig — Pipeline untuk membersihkan konfigurasi mentah.
 *
 * @example
 * const clean = sanitizeConfig(rawOmnifileContent);
 */
export const sanitizeConfig = pipe(
    removeComments,
    collapseBlankLines,
    trimLines
);

/**
 * prepareForBuild — Pipeline untuk mempersiapkan config sebelum build.
 *
 * @example
 * const ready = prepareForBuild(rawContent);
 */
export const prepareForBuild = pipe(
    removeComments,
    collapseBlankLines,
    toUpperKeys,
    injectBuildTimestamp
);

// =====================================================
// 📊 PIPELINE DEBUGGER
// =====================================================
/**
 * tap — Intip data di tengah pipeline tanpa mengubahnya.
 * Berguna untuk debugging.
 *
 * @example
 * pipeline(data,
 *     step1,
 *     tap("After step1"),  // 📡 [PIPELINE] After step1: ...data...
 *     step2,
 *     tap("After step2"),
 *     step3
 * );
 */
export function tap(label) {
    return (data) => {
        console.log(`📡 [PIPELINE] ${label}:`, typeof data === 'string' ? data.slice(0, 100) + '...' : data);
        return data; // Pass-through tanpa mutasi
    };
}

/**
 * when — Conditional pipeline step. Hanya eksekusi fn jika condition terpenuhi.
 *
 * @example
 * pipeline(config,
 *     when(config => config.includes('DEBUG'), addDebugHeaders),
 *     finalStep
 * );
 */
export function when(condition, fn) {
    return (data) => condition(data) ? fn(data) : data;
}

/**
 * tryCatch — Jalankan fn dengan error handling. Jika error, kembalikan fallback.
 *
 * @example
 * pipeline(data,
 *     tryCatch(riskyTransform, (err, data) => {
 *         console.error("Transform gagal:", err);
 *         return data; // Kembalikan data asli
 *     })
 * );
 */
export function tryCatch(fn, onError) {
    return (data) => {
        try {
            return fn(data);
        } catch (err) {
            return onError(err, data);
        }
    };
}
