import React, { useState, useEffect, useRef } from 'react';

export const StreamViewer: React.FC<{ streamId: string }> = ({ streamId }) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [status, setStatus] = useState<'DISCONNECTED' | 'CONNECTING' | 'CONNECTED'>('DISCONNECTED');
    const [bitrate, setBitrate] = useState<number>(0);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!streamId) {
            setError("Stream ID required");
            return;
        }

        setStatus('CONNECTING');
        
        // Simulating WebRTC connection setup
        const connectTimeout = setTimeout(() => {
            setStatus('CONNECTED');
            setError(null);
            
            // Start simulating bitrate changes
            const bitrateInterval = setInterval(() => {
                setBitrate(2500 + Math.floor(Math.random() * 1000));
            }, 2000);

            return () => clearInterval(bitrateInterval);
        }, 1500);

        return () => clearTimeout(connectTimeout);
    }, [streamId]);

    return (
        <div style={{ backgroundColor: '#18181b', color: '#e4e4e7', padding: '20px', borderRadius: '8px', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h2 style={{ margin: 0, color: '#a1a1aa' }}>Stream Viewer: <span style={{ color: '#fff' }}>{streamId}</span></h2>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <div style={{ 
                        width: '12px', 
                        height: '12px', 
                        borderRadius: '50%', 
                        backgroundColor: status === 'CONNECTED' ? '#22c55e' : status === 'CONNECTING' ? '#eab308' : '#ef4444' 
                    }} />
                    <span style={{ fontSize: '14px', fontWeight: 'bold' }}>{status}</span>
                </div>
            </div>

            {error && (
                <div style={{ backgroundColor: '#7f1d1d', color: '#fca5a5', padding: '12px', borderRadius: '4px', marginBottom: '16px' }}>
                    Error: {error}
                </div>
            )}

            <div style={{ 
                width: '100%', 
                aspectRatio: '16/9', 
                backgroundColor: '#000', 
                borderRadius: '8px', 
                overflow: 'hidden',
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '1px solid #3f3f46'
            }}>
                {status === 'CONNECTED' ? (
                    <>
                        <video 
                            ref={videoRef}
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                            autoPlay 
                            playsInline
                            muted
                            loop
                        >
                            {/* A dummy source just so the video element exists and shows a play state in DOM */}
                            <source src="dummy.mp4" type="video/mp4" />
                        </video>
                        <div style={{ position: 'absolute', top: '10px', right: '10px', backgroundColor: 'rgba(0,0,0,0.6)', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                            {bitrate} kbps
                        </div>
                    </>
                ) : (
                    <div style={{ color: '#52525b' }}>Awaiting video feed...</div>
                )}
            </div>

            {status === 'CONNECTED' && (
                <div style={{ marginTop: '16px', display: 'flex', gap: '12px' }}>
                    <button style={btnStyle('#3b82f6')}>Mute Audio</button>
                    <button style={btnStyle('#ef4444')}>Disconnect</button>
                </div>
            )}
        </div>
    );
};

const btnStyle = (bg: string) => ({
    backgroundColor: bg,
    color: '#fff',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold'
});
