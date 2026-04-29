import React, { useEffect, useRef, useState } from 'react';

interface StemTrack {
    name: string;
    data: Float32Array; // Normalized [-1.0, 1.0] audio data
    color: string;
    volume: number; // 0.0 to 1.0
}

interface WaveformMixerProps {
    tracks: StemTrack[];
    width: number;
    height: number;
}

export const OmniWaveformMixer: React.FC<WaveformMixerProps> = ({ tracks, width, height }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            setError('Failed to get 2D context');
            return;
        }

        try {
            // Background
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, width, height);

            if (tracks.length === 0) {
                ctx.fillStyle = '#64748b';
                ctx.font = '14px Inter';
                ctx.fillText('No stems loaded.', 20, 30);
                return;
            }

            const trackHeight = height / tracks.length;

            tracks.forEach((track, index) => {
                const yOffset = index * trackHeight;
                const midY = yOffset + trackHeight / 2;

                // Draw Track Separator
                if (index > 0) {
                    ctx.beginPath();
                    ctx.moveTo(0, yOffset);
                    ctx.lineTo(width, yOffset);
                    ctx.strokeStyle = '#334155';
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }

                // Draw Waveform
                ctx.beginPath();
                ctx.moveTo(0, midY);
                ctx.strokeStyle = track.color;
                ctx.lineWidth = 1;

                const step = Math.ceil(track.data.length / width);
                const amp = (trackHeight / 2) * track.volume * 0.9;

                for (let i = 0; i < width; i++) {
                    const dataIndex = i * step;
                    if (dataIndex < track.data.length) {
                        // Very simplified peak extraction for rendering
                        const val = track.data[dataIndex] * amp;
                        ctx.lineTo(i, midY - val);
                    }
                }
                ctx.stroke();

                // Draw Label
                ctx.fillStyle = 'white';
                ctx.font = '12px Inter, monospace';
                ctx.fillText(`${track.name.toUpperCase()} (Vol: ${(track.volume * 100).toFixed(0)}%)`, 10, yOffset + 20);
            });

        } catch (err) {
            setError(`Rendering failed: ${err}`);
        }
    }, [tracks, width, height]);

    return (
        <div className="omni-waveform-mixer rounded-lg shadow-2xl overflow-hidden border border-slate-700">
            {error ? (
                 <div className="p-4 text-red-400 font-mono text-sm">Error: {error}</div>
            ) : (
                <canvas 
                    ref={canvasRef} 
                    width={width} 
                    height={height} 
                    className="block"
                />
            )}
        </div>
    );
};
