import React, { useState, useCallback } from 'react';
import { useOmniParams, omniNavigate, OmniClient } from '../omni';
import { OMNI_TOOLS_UI } from '../configs/toolsMap';

export function OmniToolPage() {
    const { id } = useOmniParams();
    const tool = OMNI_TOOLS_UI.find(t => t.id === id);

    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState<'IDLE' | 'UPLOADING' | 'PROCESSING' | 'SUCCESS' | 'ERROR'>('IDLE');
    const [progress, setProgress] = useState(0);
    const [resultUrl, setResultUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [dragOver, setDragOver] = useState(false);

    const handleFileSelect = useCallback((selectedFile: File) => {
        setFile(selectedFile);
        setStatus('IDLE');
        setProgress(0);
        setResultUrl(null);
        setError(null);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) handleFileSelect(droppedFile);
    }, [handleFileSelect]);

    const handleExecute = useCallback(async () => {
        if (!file || !tool) return;

        setStatus('UPLOADING');
        setProgress(10);

        try {
            const result = await OmniClient.processFile(tool.id, file);
            setStatus('PROCESSING');
            setProgress(30);

            // Poll status via REST (fallback jika WebSocket belum siap)
            const pollInterval = setInterval(async () => {
                try {
                    const jobStatus = await OmniClient.getJobStatus(result.job_id);
                    setProgress(jobStatus.progress);

                    if (jobStatus.status === 'SUCCESS') {
                        clearInterval(pollInterval);
                        setStatus('SUCCESS');
                        setResultUrl(jobStatus.output_url || null);
                    } else if (jobStatus.status === 'ERROR') {
                        clearInterval(pollInterval);
                        setStatus('ERROR');
                        setError(jobStatus.error || 'Unknown error');
                    }
                } catch {
                    // Gateway belum merespons, terus polling
                }
            }, 1500);
        } catch (err: any) {
            setStatus('ERROR');
            setError(err.message);
        }
    }, [file, tool]);

    const handleDownload = useCallback(async () => {
        if (!resultUrl) return;
        const a = document.createElement('a');
        a.href = resultUrl;
        a.download = `omni_output_${id}`;
        a.click();
    }, [resultUrl, id]);

    if (!tool) {
        return (
            <div className="tool-page">
                <div className="tool-page-empty">
                    <span className="empty-icon">❌</span>
                    <h2>Tool Tidak Ditemukan</h2>
                    <p>Tool ID <code>{id}</code> tidak ada di registry.</p>
                    <button className="omni-btn" onClick={() => omniNavigate('/')}>
                        ← Kembali ke Dashboard
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="tool-page">
            {/* Breadcrumb */}
            <div className="breadcrumb">
                <button className="breadcrumb-link" onClick={() => omniNavigate('/')}>
                    ⚡ Dashboard
                </button>
                <span className="breadcrumb-sep">/</span>
                <span className="breadcrumb-current">{tool.name}</span>
            </div>

            {/* Tool Info */}
            <div className="tool-page-header">
                <h1 className="tool-page-title">{tool.name}</h1>
                <p className="tool-page-desc">{tool.description}</p>
                <div className="tool-page-meta">
                    <span className="meta-badge">{tool.category}</span>
                    <span className="meta-id">{tool.id}</span>
                    <span className="meta-accepts">{tool.accepts}</span>
                </div>
            </div>

            {/* Drop Zone */}
            <div
                className={`dropzone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
                onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
            >
                {file ? (
                    <div className="dropzone-file">
                        <span className="file-icon">📁</span>
                        <div className="file-info">
                            <span className="file-name">{file.name}</span>
                            <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                        </div>
                        <button className="file-clear" onClick={() => setFile(null)}>✕</button>
                    </div>
                ) : (
                    <div className="dropzone-empty">
                        <span className="drop-icon">📤</span>
                        <p>Seret file ke sini atau klik untuk memilih</p>
                        <span className="drop-accepts">Menerima: {tool.accepts}</span>
                    </div>
                )}
                <input
                    type="file"
                    className="dropzone-input"
                    onChange={e => {
                        const f = e.target.files?.[0];
                        if (f) handleFileSelect(f);
                    }}
                />
            </div>

            {/* Actions */}
            <div className="tool-actions">
                <button
                    className={`omni-btn primary ${!file || status === 'PROCESSING' ? 'disabled' : ''}`}
                    onClick={handleExecute}
                    disabled={!file || status === 'PROCESSING' || status === 'UPLOADING'}
                >
                    {status === 'IDLE' && '⚡ Eksekusi'}
                    {status === 'UPLOADING' && '📤 Mengunggah...'}
                    {status === 'PROCESSING' && '⏳ Memproses...'}
                    {status === 'SUCCESS' && '✅ Selesai!'}
                    {status === 'ERROR' && '❌ Gagal — Coba Lagi'}
                </button>

                {status === 'SUCCESS' && resultUrl && (
                    <button className="omni-btn success" onClick={handleDownload}>
                        💾 Unduh Hasil
                    </button>
                )}
            </div>

            {/* Progress Bar */}
            {(status === 'UPLOADING' || status === 'PROCESSING') && (
                <div className="progress-container">
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                    </div>
                    <span className="progress-text">{progress}%</span>
                </div>
            )}

            {/* Error */}
            {status === 'ERROR' && error && (
                <div className="error-box">
                    <span>⚠️</span>
                    <p>{error}</p>
                </div>
            )}
        </div>
    );
}
