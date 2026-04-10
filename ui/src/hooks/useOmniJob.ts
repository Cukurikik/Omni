import React, { useState, useEffect } from 'react';

/**
 * 🧠 useOmniJob: Hook WebSocket Anti-Badai
 * Memantau status dan progress job dari backend OMNI secara real-time.
 */
export function useOmniJob(jobId: string | null) {
    const [status, setStatus] = useState<string>('IDLE');
    const [progress, setProgress] = useState<number>(0);
    const [message, setMessage] = useState<string>('');

    useEffect(() => {
        if (!jobId) return;

        setStatus('PROCESSING');
        setProgress(0);
        setMessage('');

        // Tentukan WebSocket URL secara dinamis
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = window.location.host || 'localhost:9600';
        const ws = new WebSocket(`${wsProtocol}//${wsHost}/ws?job_id=${jobId}`);

        ws.onopen = () => {
            console.log(`🔗 [OMNI-WS] Terhubung ke job: ${jobId}`);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.progress !== undefined) {
                    setProgress(data.progress);
                }
                if (data.status) {
                    setStatus(data.status);
                }
                if (data.message) {
                    setMessage(data.message);
                }

                // Auto-close saat selesai
                if (data.status === 'COMPLETED' || data.status === 'FAILED') {
                    ws.close();
                }
            } catch (err) {
                console.warn('[OMNI-WS] Gagal parse pesan:', event.data);
            }
        };

        ws.onerror = (error) => {
            console.error(`❌ [OMNI-WS] Error pada job ${jobId}:`, error);
            setStatus('ERROR');
        };

        ws.onclose = () => {
            console.log(`🔌 [OMNI-WS] Koneksi ditutup untuk job: ${jobId}`);
        };

        return () => {
            if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
                ws.close();
            }
        };
    }, [jobId]);

    return { status, progress, message };
}
