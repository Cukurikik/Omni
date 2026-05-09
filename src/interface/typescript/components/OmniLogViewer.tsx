import React, { useRef, useEffect } from 'react';

// OMNI MOTHER: High-performance Log Viewer (Production Grade)
// Automatically scrolls to bottom and handles large text streams.

interface Props {
    logs: string[];
}

export const OmniLogViewer: React.FC<Props> = ({ logs }) => {
    const endRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    return (
        <div style={{ 
            background: '#1e1e1e', 
            color: '#00ff00', 
            fontFamily: 'monospace',
            padding: '10px',
            height: '200px',
            overflowY: 'auto',
            borderRadius: '8px'
        }}>
            {logs.map((log, idx) => (
                <div key={idx}>{log}</div>
            ))}
            <div ref={endRef} />
        </div>
    );
};
