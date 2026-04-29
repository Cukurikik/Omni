import React, { useState } from 'react';

export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

export interface FactCheckReport {
    claimId: string;
    claimText: string;
    isSupported: boolean;
    confidence: number;
    evidence: { text: string; source: string }[];
}

export const ReportViewer: React.FC = () => {
    const [report, setReport] = useState<FactCheckReport | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [claimInput, setClaimInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleVerify = async () => {
        if (!claimInput.trim()) return;
        setLoading(true);
        setError(null);
        
        try {
            // Simulated API call
            await new Promise(r => setTimeout(r, 1000));
            
            // Generate a deterministic mock result for demonstration of the UI
            const isSupported = claimInput.length % 2 === 0;
            
            setReport({
                claimId: crypto.randomUUID(),
                claimText: claimInput,
                isSupported,
                confidence: 0.88,
                evidence: [
                    { text: "The company reported a 20% increase in Q3.", source: "SEC 10-Q" }
                ]
            });
        } catch (e: any) {
            setError(e.message || "Verification failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif', backgroundColor: '#fafafa', color: '#333' }}>
            <h1>FinFact Verification Engine</h1>
            
            <div style={{ marginBottom: '20px' }}>
                <textarea 
                    value={claimInput} 
                    onChange={e => setClaimInput(e.target.value)}
                    placeholder="Enter financial claim to verify..."
                    style={{ width: '100%', height: '100px', padding: '10px' }}
                />
                <button 
                    onClick={handleVerify} 
                    disabled={loading}
                    style={{ marginTop: '10px', padding: '10px 20px', backgroundColor: '#0052cc', color: 'white', border: 'none', cursor: 'pointer' }}
                >
                    {loading ? 'Verifying...' : 'Verify Claim'}
                </button>
            </div>

            {error && <div style={{ color: 'red', padding: '10px', border: '1px solid red' }}>{error}</div>}

            {report && (
                <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px', backgroundColor: 'white' }}>
                    <h3>Verification Results</h3>
                    <div style={{ marginBottom: '10px' }}>
                        <strong>Status: </strong>
                        <span style={{ color: report.isSupported ? 'green' : 'red', fontWeight: 'bold' }}>
                            {report.isSupported ? 'SUPPORTED' : 'REFUTED'}
                        </span>
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                        <strong>Confidence: </strong> {(report.confidence * 100).toFixed(1)}%
                    </div>
                    <h4>Evidence</h4>
                    <ul>
                        {report.evidence.map((ev, i) => (
                            <li key={i}>
                                <em>"{ev.text}"</em> - <strong>{ev.source}</strong>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};
