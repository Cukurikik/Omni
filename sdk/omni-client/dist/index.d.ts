export interface OmniJobResult {
    job_id: string;
    status: string;
}
export declare class OmniClient {
    private static baseUrl;
    /**
     * Konfigurasi URL Server OMNI-OS
     * @param url - Base URL Backend
     */
    static setBaseUrl(url: string): void;
    /**
     * Mengirim file ke backend untuk diforger oleh API (OMNI-KINETIC/Blackbox)
     * @param toolName - Nama alat (contoh: "image_blur", "video_trim")
     * @param file - Objek File/Blob yang akan diupload
     * @returns - Job ID untuk status tracking via WebSocket
     */
    static processFile(toolName: string, file: File | Blob): Promise<OmniJobResult>;
}
