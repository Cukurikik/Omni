#!/usr/bin/env node
// =====================================================
// 📜 OMNI-SPHERE: THE OMNIFILE PARSER ENGINE
// =====================================================
// Membaca file konfigurasi "Omnifile" (tanpa ekstensi)
// dengan Sintaks Kedaulatan OMNI dan menerjemahkannya
// menjadi objek JavaScript terstruktur.
//
// Sintaks yang didukung:
//   # Komentar
//   KEY "string value"
//   KEY 123              (number)
//   KEY true|false        (boolean)
//   BLOCK_NAME:          (array block dengan - prefix)
//     - item_1
//     - item_2
//   KEY_VALUE_BLOCK:     (key-value pairs)
//     SUBKEY "value"
// =====================================================

import { existsSync, readFileSync } from 'fs';
import { join } from 'path';

/**
 * @typedef {Object} OmnifileConfig
 * @property {string} APP_NAME
 * @property {string} VERSION
 * @property {number} PORT
 * @property {string} THEME
 * @property {string[]} REQUIRE_TOOLS
 * @property {number} MAX_UPLOAD_GB
 * @property {string} MAX_RAM_USAGE
 * @property {boolean} PERSISTENCE
 * @property {string} ENVIRONMENT
 * @property {Record<string, string>} ENV
 * @property {string} NEXUS_ROLE
 * @property {string} NEXUS_SECRET
 */

// =====================================================
// 🔍 LOKATOR: Menemukan Omnifile terdekat
// =====================================================
/**
 * Mencari Omnifile di direktori yang diberikan atau CWD.
 * Mendukung nama: Omnifile, omnifile, OMNIFILE, .omnifile
 * @param {string} [searchDir] — Direktori pencarian (default: CWD)
 * @returns {string|null} — Path absolut ke Omnifile, atau null jika tidak ditemukan
 */
export function locateOmnifile(searchDir) {
    const dir = searchDir || process.cwd();
    const candidates = ['Omnifile', 'omnifile', 'OMNIFILE', '.omnifile'];

    for (const name of candidates) {
        const fullPath = join(dir, name);
        if (existsSync(fullPath)) {
            return fullPath;
        }
    }
    return null;
}

// =====================================================
// 🧠 PARSER CORE: Mentranslasi Sintaks Kedaulatan
// =====================================================

/**
 * Parse nilai tunggal dari string mentah.
 * "hello world" → 'hello world'
 * 123          → 123
 * true         → true
 * @param {string} raw
 * @returns {string|number|boolean}
 */
function parseValue(raw) {
    const trimmed = raw.trim();

    // Boolean
    if (trimmed === 'true') return true;
    if (trimmed === 'false') return false;

    // Number (integer atau float)
    if (/^-?\d+(\.\d+)?$/.test(trimmed)) {
        return Number(trimmed);
    }

    // Quoted string — hapus tanda kutip
    const quoted = trimmed.match(/^"(.*)"$/);
    if (quoted) return quoted[1];

    // Single-quoted string
    const singleQuoted = trimmed.match(/^'(.*)'$/);
    if (singleQuoted) return singleQuoted[1];

    // Raw string (tanpa tanda kutip)
    return trimmed;
}

/**
 * Parse isi file Omnifile menjadi objek config terstruktur.
 * @param {string} content — Isi mentah file Omnifile
 * @returns {OmnifileConfig}
 */
export function parseOmnifileContent(content) {
    const lines = content.split('\n');
    const config = {};

    let currentBlock = null;      // Nama block aktif (contoh: 'REQUIRE_TOOLS')
    let blockType = null;         // 'array' atau 'map'

    for (let i = 0; i < lines.length; i++) {
        const rawLine = lines[i];
        const line = rawLine.trimEnd();

        // === Lewati baris kosong dan komentar ===
        if (line.trim() === '' || line.trim().startsWith('#')) {
            // Baris kosong setelah block → akhiri block
            if (line.trim() === '' && currentBlock) {
                // Periksa baris berikutnya: jika bukan indented, akhiri block
                const nextLine = (i + 1 < lines.length) ? lines[i + 1] : '';
                if (!nextLine.match(/^\s+(- |[A-Z_])/)) {
                    currentBlock = null;
                    blockType = null;
                }
            }
            continue;
        }

        // === Deteksi indentasi (baris dalam block) ===
        const indent = line.match(/^(\s+)/);
        const isIndented = indent && indent[1].length >= 2;

        if (isIndented && currentBlock) {
            const innerContent = line.trim();

            if (blockType === 'array') {
                // Array item: - value
                const arrayMatch = innerContent.match(/^-\s+(.+)$/);
                if (arrayMatch) {
                    config[currentBlock].push(parseValue(arrayMatch[1]));
                }
            } else if (blockType === 'map') {
                // Key-value pair: SUBKEY "value" atau SUBKEY value
                const kvMatch = innerContent.match(/^([A-Za-z_][A-Za-z0-9_]*)\s+(.+)$/);
                if (kvMatch) {
                    config[currentBlock][kvMatch[1]] = parseValue(kvMatch[2]);
                }
            }
            continue;
        }

        // === Baris tidak ter-indent → akhiri block sebelumnya ===
        if (currentBlock && !isIndented) {
            currentBlock = null;
            blockType = null;
        }

        // === Deteksi BLOCK_NAME: (diakhiri titik dua) ===
        const blockMatch = line.match(/^([A-Z_][A-Z0-9_]*):$/);
        if (blockMatch) {
            const blockName = blockMatch[1];

            // Tentukan tipe block dari baris berikutnya
            const nextLine = (i + 1 < lines.length) ? lines[i + 1].trim() : '';
            if (nextLine.startsWith('-')) {
                // Array block
                config[blockName] = [];
                currentBlock = blockName;
                blockType = 'array';
            } else {
                // Map block (key-value pairs)
                config[blockName] = {};
                currentBlock = blockName;
                blockType = 'map';
            }
            continue;
        }

        // === KEY VALUE (top-level) ===
        const kvMatch = line.match(/^([A-Za-z_][A-Za-z0-9_]*)\s+(.+)$/);
        if (kvMatch) {
            const key = kvMatch[1];
            const value = parseValue(kvMatch[2]);
            config[key] = value;
            continue;
        }

        // === KEY tanpa VALUE (flag boolean implisit) ===
        const flagMatch = line.match(/^([A-Z_][A-Z0-9_]*)$/);
        if (flagMatch) {
            config[flagMatch[1]] = true;
            continue;
        }
    }

    return config;
}

/**
 * Parse file Omnifile dari path absolut.
 * @param {string} filePath
 * @returns {OmnifileConfig}
 */
export function parseOmnifile(filePath) {
    if (!existsSync(filePath)) {
        throw new Error(`Omnifile tidak ditemukan di: ${filePath}`);
    }

    const content = readFileSync(filePath, 'utf8');
    return parseOmnifileContent(content);
}

// =====================================================
// 🔁 TRANSFORMER: Config → appconfig.json format
// =====================================================
/**
 * Mengkonversi OmnifileConfig menjadi format appconfig.json
 * yang kompatibel dengan Golang Gateway.
 * @param {OmnifileConfig} omniConfig
 * @returns {object} — appconfig.json compatible object
 */
export function toAppConfig(omniConfig) {
    return {
        app_name: omniConfig.APP_NAME || 'OMNI Project',
        version: omniConfig.VERSION || '1.0.0',
        environment: omniConfig.ENVIRONMENT || 'development',
        server: {
            host: '0.0.0.0',
            port: omniConfig.PORT || 3000,
            read_timeout_seconds: 60,
            write_timeout_seconds: 3600,
            graceful_shutdown_seconds: 10,
        },
        security: {
            session_secret:
                (omniConfig.ENV && omniConfig.ENV.OMNI_SECRET) ||
                'OMNI_SECRET_' + Math.random().toString(36).slice(2, 14),
            cors_allowed_origins: ['*'],
            rate_limit_per_second: 20,
            enable_coop_coep: true,
        },
        storage: {
            max_upload_gb: omniConfig.MAX_UPLOAD_GB || 50,
            quarantine_dir: '../release/omni_quarantine',
            cache_dir: '../release/omni_cache',
            cache_ttl_minutes: 60,
        },
        engine: {
            max_concurrent_workers: 4,
            go_workers: 8,
            ffmpeg_throttle_threads: 2,
            job_cleanup_hours: 24,
        },
        features: {
            live_reload: omniConfig.ENVIRONMENT !== 'production',
            telemetry: true,
            auto_heal: true,
            persistence: omniConfig.PERSISTENCE === true,
        },
        firebase: {
            enabled: !!(omniConfig.ENV && omniConfig.ENV.FIREBASE_PROJECT),
            credentials_path: '../configs/serviceAccountKey.json',
            project_id: (omniConfig.ENV && omniConfig.ENV.FIREBASE_PROJECT) || '',
        },
        nexus_cluster: {
            role: omniConfig.NEXUS_ROLE || 'standalone',
            master_url:
                omniConfig.NEXUS_MASTER_URL ||
                `http://127.0.0.1:${omniConfig.PORT || 3000}`,
            cluster_secret:
                omniConfig.NEXUS_SECRET || 'OMNI_NEXUS_DEFAULT_KEY',
            worker_max_jobs: 2,
            heartbeat_interval_seconds: 5,
            dead_threshold_seconds: 15,
        },
    };
}

// =====================================================
// 🖨️ PRETTY PRINTER: Tampilan Manusiawi
// =====================================================
/**
 * Cetak isi OmnifileConfig ke console dengan format militer.
 * @param {OmnifileConfig} config
 */
export function prettyPrintConfig(config) {
    console.log('\n' + '='.repeat(60));
    console.log('📜 OMNIFILE — PARSED CONFIGURATION');
    console.log('='.repeat(60));

    for (const [key, value] of Object.entries(config)) {
        if (Array.isArray(value)) {
            console.log(`\n  📋 ${key}:`);
            value.forEach((item) => console.log(`     - ${item}`));
        } else if (typeof value === 'object' && value !== null) {
            console.log(`\n  📦 ${key}:`);
            for (const [k, v] of Object.entries(value)) {
                console.log(`     ${k} = ${JSON.stringify(v)}`);
            }
        } else {
            const icon =
                typeof value === 'boolean'
                    ? value ? '✅' : '❌'
                    : typeof value === 'number'
                      ? '🔢'
                      : '📝';
            console.log(`  ${icon} ${key} = ${JSON.stringify(value)}`);
        }
    }

    console.log('\n' + '='.repeat(60) + '\n');
}

// =====================================================
// 📜 GENERATOR: Membuat Omnifile dari konfigurasi
// =====================================================
/**
 * Generate konten Omnifile dari objek config.
 * Berguna untuk `omni init` yang membuat Omnifile default.
 * @param {Partial<OmnifileConfig>} config
 * @returns {string}
 */
export function generateOmnifileContent(config) {
    let content = '';
    content += '# ===================================\n';
    content += '# OMNI FRAMEWORK MANIFEST\n';
    content += `# Generated: ${new Date().toISOString()}\n`;
    content += '# ===================================\n\n';

    // Top-level scalars
    const scalarKeys = Object.keys(config).filter((k) => {
        const v = config[k];
        return typeof v !== 'object' || v === null;
    });

    for (const key of scalarKeys) {
        const val = config[key];
        if (typeof val === 'string') {
            content += `${key} "${val}"\n`;
        } else {
            content += `${key} ${val}\n`;
        }
    }

    // Array blocks
    const arrayKeys = Object.keys(config).filter((k) =>
        Array.isArray(config[k]),
    );
    for (const key of arrayKeys) {
        content += `\n${key}:\n`;
        for (const item of config[key]) {
            content += `  - ${item}\n`;
        }
    }

    // Map blocks
    const mapKeys = Object.keys(config).filter((k) => {
        const v = config[k];
        return typeof v === 'object' && v !== null && !Array.isArray(v);
    });
    for (const key of mapKeys) {
        content += `\n${key}:\n`;
        for (const [k, v] of Object.entries(config[key])) {
            if (typeof v === 'string') {
                content += `  ${k} "${v}"\n`;
            } else {
                content += `  ${k} ${v}\n`;
            }
        }
    }

    return content;
}
