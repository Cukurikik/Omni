// ==========================================
// 🛡️ OMNI-SDK: Frontend Integration Client
// ==========================================

export interface OmniJobResult {
    job_id: string;
    status: string;
}

export class OmniClient {
    private static baseUrl = 'http://localhost:8080/api/v1'; // Default API Host

    /**
     * Konfigurasi URL Server OMNI-OS 
     * @param url - Base URL Backend
     */
    static setBaseUrl(url: string) {
        this.baseUrl = url;
    }

    /**
     * Mengirim file ke backend untuk diforger oleh API (OMNI-KINETIC/Blackbox)
     * @param toolName - Nama alat (contoh: "image_blur", "video_trim")
     * @param file - Objek File/Blob yang akan diupload
     * @returns - Job ID untuk status tracking via WebSocket
     */
    static async processFile(toolName: string, file: File | Blob): Promise<OmniJobResult> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseUrl}/forge/${toolName}`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`[OMNI-SDK] Gagal memproses file pada tool ${toolName}`);
        }

        return await response.json();
    }
}
