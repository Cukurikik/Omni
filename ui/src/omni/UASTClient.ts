// ==========================================
// 🔌 OMNI TELEPATHY — UAST CLIENT (Universal Abstract Syntax Tree)
// ==========================================
// Mengimplementasikan instruksi Monadic yang menghubungkan UI (TypeScript)
// ke Gateway Inti (Golang) dan diteruskan ke Runtime (C++/Rust/Python).
// ==========================================

export const OMNI_API_BASE = '';

/** Monadic Result Tipe Sesuai Standar Blueprint OMNI */
export type Result<T, E> = 
  | { status: 'Ok'; data: T }
  | { status: 'Err'; error: E };

export interface OmniRequest {
    method: string;
    args: Record<string, any>;
}

export interface OmniResponse<T = any> {
    status: 'Ok' | 'Err';
    data?: T;
    error?: string;
}

export const UASTClient = {
    /**
     * Mengeksekusi instruksi Telepathy menuju Core Gateway Golang.
     * Tidak menggunakan try/catch mematikan, mengembalikan Monadic Result.
     */
    async invoke<T = any>(method: string, args: Record<string, any> = {}): Promise<Result<T, string>> {
        const payload: OmniRequest = { method, args };

        const res = await fetch(`${OMNI_API_BASE}/api/v1/invoke`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // API Key harus disuntikkan secara dinamis pada sesi tertutup
                'X-Omni-Api-Key': 'omni-dev-key' 
            },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            return { status: 'Err', error: `Network Gateway Error: ${res.status}` };
        }

        const data: OmniResponse<T> = await res.json();
        
        if (data.status === 'Err') {
            return { status: 'Err', error: data.error || 'Unknown Gateway Error' };
        }

        return { status: 'Ok', data: data.data as T };
    },

    /**
     * Health Pinger Khusus Gateway Nodes.
     */
    async ping(): Promise<Result<boolean, string>> {
        const res = await fetch(`${OMNI_API_BASE}/health`);
        if (!res.ok) return { status: 'Err', error: 'Gateway Offline' };
        
        const data = await res.json();
        return { status: 'Ok', data: data.status === 'Ok' };
    }
};
