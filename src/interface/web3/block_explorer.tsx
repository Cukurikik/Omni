import React, { useState, useEffect } from 'react';

export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

interface Block {
    number: number;
    hash: string;
    parentHash: string;
    timestamp: number;
    txCount: number;
    proposer: string;
}

export const BlockExplorer: React.FC = () => {
    const [blocks, setBlocks] = useState<Block[]>([]);
    const [latestBlock, setLatestBlock] = useState<number>(100000);

    const generateHash = () => {
        return '0x' + Array.from({length: 64}, () => Math.floor(Math.random()*16).toString(16)).join('');
    };

    useEffect(() => {
        // Simulate block production every 3 seconds (Tendermint style)
        const interval = setInterval(() => {
            setLatestBlock(prev => {
                const next = prev + 1;
                
                const newBlock: Block = {
                    number: next,
                    hash: generateHash(),
                    parentHash: blocks.length > 0 ? blocks[0].hash : generateHash(),
                    timestamp: Date.now(),
                    txCount: Math.floor(Math.random() * 500),
                    proposer: `Validator-${Math.floor(Math.random() * 21)}`
                };

                setBlocks(currentBlocks => [newBlock, ...currentBlocks].slice(0, 10));
                return next;
            });
        }, 3000);

        return () => clearInterval(interval);
    }, [blocks]);

    return (
        <div style={{ backgroundColor: '#0f172a', color: '#f8fafc', padding: '24px', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
            <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
                <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', borderBottom: '1px solid #1e293b', paddingBottom: '16px' }}>
                    <h1 style={{ color: '#38bdf8', margin: 0, display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ width: '16px', height: '16px', backgroundColor: '#10b981', borderRadius: '4px', animation: 'pulse 2s infinite' }}></div>
                        OmniScan Explorer
                    </h1>
                    <div style={{ backgroundColor: '#1e293b', padding: '8px 16px', borderRadius: '20px', fontSize: '14px', fontWeight: 'bold' }}>
                        Network: Mainnet
                    </div>
                </header>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '32px' }}>
                    <StatCard title="LATEST BLOCK" value={`#${latestBlock.toLocaleString()}`} />
                    <StatCard title="TPS (LIVE)" value={`${Math.floor(Math.random() * 100 + 50)}`} />
                    <StatCard title="ACTIVE VALIDATORS" value="21 / 21" />
                </div>

                <div style={{ backgroundColor: '#1e293b', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
                    <div style={{ padding: '16px 24px', borderBottom: '1px solid #334155', fontWeight: 'bold' }}>
                        Latest Blocks
                    </div>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
                        <thead style={{ backgroundColor: '#0f172a', color: '#94a3b8' }}>
                            <tr>
                                <th style={{ padding: '12px 24px' }}>Block</th>
                                <th style={{ padding: '12px 24px' }}>Hash</th>
                                <th style={{ padding: '12px 24px' }}>Age</th>
                                <th style={{ padding: '12px 24px' }}>Txn</th>
                                <th style={{ padding: '12px 24px' }}>Proposer</th>
                            </tr>
                        </thead>
                        <tbody>
                            {blocks.map((block) => (
                                <tr key={block.number} style={{ borderBottom: '1px solid #334155' }}>
                                    <td style={{ padding: '16px 24px', color: '#38bdf8', fontWeight: 'bold' }}>{block.number}</td>
                                    <td style={{ padding: '16px 24px', fontFamily: 'monospace', color: '#cbd5e1' }}>
                                        {block.hash.substring(0, 16)}...
                                    </td>
                                    <td style={{ padding: '16px 24px', color: '#94a3b8' }}>
                                        {Math.floor((Date.now() - block.timestamp) / 1000)}s ago
                                    </td>
                                    <td style={{ padding: '16px 24px' }}>
                                        <span style={{ backgroundColor: '#334155', padding: '2px 8px', borderRadius: '12px' }}>
                                            {block.txCount}
                                        </span>
                                    </td>
                                    <td style={{ padding: '16px 24px', color: '#10b981' }}>{block.proposer}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
            <style>{`
                @keyframes pulse {
                    0% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.5; transform: scale(0.9); }
                    100% { opacity: 1; transform: scale(1); }
                }
            `}</style>
        </div>
    );
};

const StatCard: React.FC<{title: string, value: string}> = ({title, value}) => (
    <div style={{ backgroundColor: '#1e293b', padding: '24px', borderRadius: '8px' }}>
        <div style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold', marginBottom: '8px' }}>{title}</div>
        <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#f8fafc' }}>{value}</div>
    </div>
);
