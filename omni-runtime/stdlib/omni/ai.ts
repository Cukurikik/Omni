// ==========================================
// 🤖 OMNI-LAND: NATIVE AI INFERENCE
// ==========================================
// AI yang berjalan 100% LOKAL di server Anda.
// Tidak perlu koneksi internet. Tidak ada biaya API per token.
// Keamanan data 100% karena teks TIDAK PERNAH meninggalkan server.
//
// IMPORT: import { askOmniMind, getAIStatus } from 'omni/ai';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

export interface AIResponse {
    text: string;
    model: string;
    tokens_generated: number;
    latency_ms: number;
    mode: 'local' | 'stub';
    cost: string;
}

export interface AIConfig {
    maxTokens?: number;
    temperature?: number;
    topP?: number;
    contextSize?: number;
    threads?: number;
}

/**
 * ⚡ SPEK DEWA: Menjalankan AI secara LOKAL di server.
 * Tidak perlu koneksi internet. Tidak ada biaya API per token.
 * Keamanan data 100% karena teks tidak pernah meninggalkan server Anda.
 *
 * @param prompt - Pertanyaan atau instruksi untuk AI
 * @param context - Konteks tambahan (opsional)
 * @param maxTokens - Maks token output (default: 512)
 *
 * @example
 * ```ts
 * import { askOmniMind } from 'omni/ai';
 *
 * const ringkasan = askOmniMind(
 *     "Ringkas artikel ini dalam 3 kalimat:",
 *     artikelPanjang
 * );
 * console.log(ringkasan);
 * ```
 */
export function askOmniMind(prompt: string, context?: string, maxTokens?: number): string {
    const raw = OmniNative.syscall("ai_infer", {
        prompt,
        context: context ?? "",
        max_tokens: maxTokens ?? 512,
    });

    if (raw.error) {
        throw new Error(`[OMNI-MIND] Inferensi gagal: ${raw.error}`);
    }

    return (raw as unknown as AIResponse).text;
}

/**
 * Jalankan AI dan dapatkan response lengkap (termasuk metadata).
 */
export function askOmniMindFull(prompt: string, context?: string, maxTokens?: number): AIResponse {
    const raw = OmniNative.syscall("ai_infer", {
        prompt,
        context: context ?? "",
        max_tokens: maxTokens ?? 512,
    });

    if (raw.error) {
        throw new Error(`[OMNI-MIND] Inferensi gagal: ${raw.error}`);
    }

    return raw as unknown as AIResponse;
}

/**
 * Startup OMNI-MIND engine dengan model GGUF tertentu.
 * Biasanya dipanggil saat server boot.
 */
export function awakenOmniMind(modelPath: string, threads?: number, contextSize?: number): void {
    const raw = OmniNative.syscall("ai_awaken", {
        model_path: modelPath,
        threads: threads ?? 4,
        context_size: contextSize ?? 2048,
    });

    if (raw.error) {
        throw new Error(`[OMNI-MIND] Gagal memuat model: ${raw.error}`);
    }

    console.log(`🧠 [OMNI-MIND] Model dimuat: ${modelPath}`);
}

/**
 * Dapatkan status AI engine saat ini.
 */
export function getAIStatus(): Record<string, unknown> {
    return OmniNative.syscall("ai_status", {});
}

export default { askOmniMind, askOmniMindFull, awakenOmniMind, getAIStatus };
