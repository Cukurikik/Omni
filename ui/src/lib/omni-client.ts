/**
 * 🌐 OMNI-OS Client SDK
 * Abstraksi komunikasi dengan OMNI Gateway Backend.
 * Menggantikan fetch/axios manual dengan API yang bersih.
 */

const BASE_URL = typeof window !== 'undefined' 
    ? `${window.location.protocol}//${window.location.host}` 
    : 'http://localhost:9600';

export const OmniClient = {
    /**
     * Mengirim file ke backend untuk diproses oleh tool tertentu.
     * @param toolId - ID tool dari cli_registry (contoh: 'ai_vision', 'brain')
     * @param file - File yang akan diproses
     * @param options - Opsi tambahan (opsional)
     */
    async processFile(toolId: string, file: File, options?: Record<string, unknown>) {
        const formData = new FormData();
        formData.append('file', file);
        
        if (options) {
            formData.append('options', JSON.stringify(options));
        }

        const response = await fetch(`${BASE_URL}/api/v1/omni/execute?tool_id=${toolId}`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`OMNI Gateway Error: ${response.status} ${response.statusText}`);
        }

        return response.json();
    },

    /**
     * Mengirim pesan ke backend (untuk tool LLM/Chat).
     */
    async sendMessage(toolId: string, message: string, context?: unknown[]) {
        const response = await fetch(`${BASE_URL}/api/v1/omni/execute?tool_id=${toolId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, context }),
        });

        if (!response.ok) {
            throw new Error(`OMNI Gateway Error: ${response.status} ${response.statusText}`);
        }

        return response.json();
    },

    /**
     * Emit event via WebSocket (fire-and-forget).
     * Digunakan untuk state sync antara UI dan backend.
     */
    emit(event: string, data: unknown) {
        // Jika WebSocket belum tersedia, log saja
        console.log(`[OMNI-CLIENT] emit('${event}')`, data);
    },

    /**
     * Mendapatkan URL download untuk hasil job.
     */
    getDownloadUrl(jobId: string): string {
        return `${BASE_URL}/api/v1/omni/download?job_id=${jobId}`;
    },
};

export default OmniClient;
