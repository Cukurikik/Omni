import React from 'react';

// OMNI MemGPT: Memory Viewer UI
// React component to visualize the OS-like memory tiers of an agent.
// Source: memgpt/MemGPT

interface MemoryProps {
    coreLimit: number;
    currentTokens: number;
    personaBlocks: string[];
    humanBlocks: string[];
    messageQueue: string[];
    archivalCount: number;
}

export const MemoryViewer: React.FC<MemoryProps> = ({
    coreLimit, currentTokens, personaBlocks, humanBlocks, messageQueue, archivalCount
}) => {
    
    const usagePercent = Math.min(100, (currentTokens / coreLimit) * 100);
    const usageColor = usagePercent > 90 ? '#e74c3c' : usagePercent > 70 ? '#f39c12' : '#2ecc71';

    return (
        <div style={{ fontFamily: 'monospace', backgroundColor: '#1e1e1e', color: '#d4d4d4', padding: '20px', borderRadius: '8px' }}>
            <h2 style={{ color: '#569cd6', borderBottom: '1px solid #333', paddingBottom: '10px' }}>MemGPT: Virtual Memory OS</h2>
            
            {/* Memory Usage Bar */}
            <div style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                    <span>Working Context Usage</span>
                    <span>{currentTokens} / {coreLimit} Tokens</span>
                </div>
                <div style={{ width: '100%', backgroundColor: '#333', height: '15px', borderRadius: '5px', overflow: 'hidden' }}>
                    <div style={{ width: `${usagePercent}%`, backgroundColor: usageColor, height: '100%', transition: 'width 0.3s' }} />
                </div>
            </div>

            <div style={{ display: 'flex', gap: '20px' }}>
                {/* Core Memory (Pinned) */}
                <div style={{ flex: 1, backgroundColor: '#252526', padding: '15px', borderRadius: '5px', border: '1px solid #444' }}>
                    <h3 style={{ color: '#c586c0', marginTop: 0 }}>Core Memory (Page Locked)</h3>
                    <div>
                        <strong style={{ color: '#9cdcfe' }}>[Persona]</strong>
                        <ul style={{ paddingLeft: '20px', margin: '5px 0' }}>
                            {personaBlocks.map((b, i) => <li key={i}>{b}</li>)}
                        </ul>
                    </div>
                    <div style={{ marginTop: '10px' }}>
                        <strong style={{ color: '#9cdcfe' }}>[Human]</strong>
                        <ul style={{ paddingLeft: '20px', margin: '5px 0' }}>
                            {humanBlocks.map((b, i) => <li key={i}>{b}</li>)}
                        </ul>
                    </div>
                </div>

                {/* Recall / Working Memory (FIFO) */}
                <div style={{ flex: 1, backgroundColor: '#252526', padding: '15px', borderRadius: '5px', border: '1px solid #444' }}>
                    <h3 style={{ color: '#4ec9b0', marginTop: 0 }}>Recall Memory (Evictable)</h3>
                    <div style={{ maxHeight: '200px', overflowY: 'auto', fontSize: '0.9em' }}>
                        {messageQueue.map((msg, i) => (
                            <div key={i} style={{ padding: '5px', borderBottom: '1px solid #333' }}>
                                {msg.substring(0, 60)}{msg.length > 60 ? '...' : ''}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Archival Stats */}
            <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#000', borderRadius: '5px', textAlign: 'center', color: '#ce9178' }}>
                <span style={{ fontSize: '1.2em' }}>🗄️ Archival Memory (Disk/VectorDB): <strong>{archivalCount}</strong> objects</span>
            </div>
        </div>
    );
};
