import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

// 1. Deteksi Bahasa Sistem (Fallback ke 'en' jika tidak dikenali)
// Di Node.js, kita bisa membaca environment variable LANG (contoh: en_US.UTF-8 atau id_ID)
const sysLang = (process.env.LANG || process.env.LANGUAGE || 'en').substring(0, 2);
const ROOT_DIR = process.cwd();

// Baca config user, siapa tahu mereka memaksa pakai bahasa tertentu
const configPath = join(ROOT_DIR, 'configs/appconfig.json');
let userLang = sysLang;
if (existsSync(configPath)) {
    const config = JSON.parse(readFileSync(configPath, 'utf8'));
    if (config.cli_language) userLang = config.cli_language;
}

// 2. Muat Kamus ke Memori
const localePath = join(ROOT_DIR, `configs/locales/${userLang}.json`);
const defaultLocalePath = join(ROOT_DIR, `configs/locales/en.json`);

let dictionary = {};
try {
    dictionary = JSON.parse(readFileSync(existsSync(localePath) ? localePath : defaultLocalePath, 'utf8'));
} catch (e) {
    console.error("❌ Fatal Error: OMNI-LINGUA dictionary missing!");
    process.exit(1);
}

// 3. Fungsi Translate Utama (The 't' function)
export function t(key, variables = {}) {
    let text = dictionary[key] || `[MISSING_TRANSLATION: ${key}]`;
    
    // Ganti variabel seperti {{tool_name}} dengan nilai dari objek 'variables'
    for (const [varName, varValue] of Object.entries(variables)) {
        const regex = new RegExp(`{{${varName}}}`, 'g');
        text = text.replace(regex, varValue);
    }
    
    return text;
}
