// ==========================================
// 🔌 OMNI-CLIENT: HTTP & WebSocket SDK
// ==========================================
// SDK internal untuk berkomunikasi dengan Golang Gateway.
// Semua komponen UI menggunakan ini — bukan fetch/axios langsung.

export const OMNI_API_BASE = '';  // Sama-origin (Golang serve di port yang sama)

export interface OmniJobResult {
    job_id: string;
    status: string;
    message?: string;
}

export interface OmniJobStatus {
    job_id: string;
    status: 'QUEUED' | 'PROCESSING' | 'SUCCESS' | 'ERROR';
    progress: number;
    output_url?: string;
    error?: string;
}

// ==========================================
// HTTP CLIENT
// ==========================================
export const OmniClient = {
    /**
     * Kirim file ke Gateway untuk diproses oleh tool tertentu.
     */
    async processFile(toolId: string, file: File, extraParams?: Record<string, string>): Promise<OmniJobResult> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('tool_id', toolId);

        if (extraParams) {
            Object.entries(extraParams).forEach(([key, value]) => {
                formData.append(key, value);
            });
        }

        const res = await fetch(`${OMNI_API_BASE}/api/v1/tools/universal/execute`, {
            method: 'POST',
            body: formData,
        });

        if (!res.ok) {
            const text = await res.text();
            throw new Error(`OMNI Gateway Error: ${res.status} - ${text}`);
        }

        return res.json();
    },

    /**
     * Cek status job langsung via REST (polling fallback).
     */
    async getJobStatus(jobId: string): Promise<OmniJobStatus> {
        const res = await fetch(`${OMNI_API_BASE}/api/v1/jobs/${jobId}/status`);
        if (!res.ok) throw new Error(`Job status error: ${res.status}`);
        return res.json();
    },

    /**
     * Download file hasil pemrosesan.
     */
    async downloadResult(jobId: string): Promise<Blob> {
        const res = await fetch(`${OMNI_API_BASE}/api/v1/jobs/${jobId}/download`);
        if (!res.ok) throw new Error(`Download error: ${res.status}`);
        return res.blob();
    },

    /**
     * Health check Gateway.
     */
    async ping(): Promise<boolean> {
        try {
            const res = await fetch(`${OMNI_API_BASE}/api/v1/health`);
            return res.ok;
        } catch {
            return false;
        }
    }
};

// ==========================================
// WEBSOCKET (OMNI-RESONANCE)
// ==========================================
export function createOmniSocket(jobId: string, onUpdate: (data: OmniJobStatus) => void): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/job/${jobId}`);

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            onUpdate(data);
        } catch {
            // Sinyal reload dari OMNI-RESONANCE, abaikan
        }
    };

    return ws;
}
