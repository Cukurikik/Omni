import React, { useState, useEffect } from 'react';

// OMNI Monadic Type
export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

export interface DocumentMeta {
    id: string;
    title: string;
    uploadedAt: string;
    status: 'INDEXING' | 'SYNCED' | 'FAILED';
    tokenCount: number;
}

export const KnowledgeBase: React.FC = () => {
    const [documents, setDocuments] = useState<DocumentMeta[]>([]);
    const [uploading, setUploading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const fetchDocuments = async (): Promise<MonadicResult<DocumentMeta[], string>> => {
        try {
            const res = await fetch('/api/memory/documents');
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            const data = await res.json();
            return { success: true, value: data };
        } catch (e: any) {
            return { success: false, error: e.message };
        }
    };

    useEffect(() => {
        fetchDocuments().then(res => {
            if (res.success) {
                setDocuments(res.value);
            } else {
                setError(res.error);
            }
        });
    }, []);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/memory/upload', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
            
            // Refresh list
            const docs = await fetchDocuments();
            if (docs.success) setDocuments(docs.value);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setUploading(false);
            if (e.target) e.target.value = '';
        }
    };

    return (
        <div className="knowledge-base" style={{ padding: '2rem', background: '#1e1e1e', color: '#e0e0e0', minHeight: '100vh' }}>
            <h1 style={{ borderBottom: '1px solid #444', paddingBottom: '1rem' }}>OMNI Knowledge Base (RAG)</h1>
            
            {error && <div style={{ background: '#4a1111', color: '#ffaaaa', padding: '1rem', margin: '1rem 0', borderRadius: '4px' }}>
                Error: {error}
            </div>}

            <div className="upload-section" style={{ margin: '2rem 0' }}>
                <label style={{ display: 'inline-block', background: '#2196F3', color: 'white', padding: '10px 20px', cursor: 'pointer', borderRadius: '4px' }}>
                    {uploading ? 'Processing...' : 'Upload Document'}
                    <input type="file" accept=".txt,.md,.pdf" style={{ display: 'none' }} onChange={handleFileUpload} disabled={uploading} />
                </label>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                    <tr style={{ borderBottom: '2px solid #444' }}>
                        <th style={{ padding: '10px' }}>Title</th>
                        <th style={{ padding: '10px' }}>Tokens</th>
                        <th style={{ padding: '10px' }}>Status</th>
                        <th style={{ padding: '10px' }}>Uploaded At</th>
                    </tr>
                </thead>
                <tbody>
                    {documents.length === 0 ? (
                        <tr><td colSpan={4} style={{ padding: '20px', textAlign: 'center', color: '#888' }}>No documents in memory store.</td></tr>
                    ) : (
                        documents.map(doc => (
                            <tr key={doc.id} style={{ borderBottom: '1px solid #333' }}>
                                <td style={{ padding: '10px' }}>{doc.title}</td>
                                <td style={{ padding: '10px' }}>{doc.tokenCount.toLocaleString()}</td>
                                <td style={{ padding: '10px' }}>
                                    <span style={{ 
                                        padding: '4px 8px', borderRadius: '12px', fontSize: '0.8rem',
                                        background: doc.status === 'SYNCED' ? '#1b5e20' : doc.status === 'INDEXING' ? '#e65100' : '#b71c1c'
                                    }}>
                                        {doc.status}
                                    </span>
                                </td>
                                <td style={{ padding: '10px' }}>{new Date(doc.uploadedAt).toLocaleString()}</td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );
};
