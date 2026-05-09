import React, { useEffect, useRef } from 'react';

// OmniOscilloscope.tsx — Time-Domain Waveform Visualizer
// Layer: Interface / TypeScript
//
// Hooks into the browser's Web Audio API AnalyserNode to render
// a real-time time-domain waveform (oscilloscope) on an HTML5 Canvas. Zero mock.

export interface OmniOscilloscopeProps {
    audioContext: AudioContext;
    sourceNode: AudioNode;
    width: number;
    height: number;
    lineColor?: string;
    lineWidth?: number;
    className?: string;
}

export const OmniOscilloscope: React.FC<OmniOscilloscopeProps> = ({
    audioContext,
    sourceNode,
    width,
    height,
    lineColor = '#10b981', // Tailwind emerald-500
    lineWidth = 2,
    className = ''
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const requestRef = useRef<number>();
    const analyserRef = useRef<AnalyserNode | null>(null);

    useEffect(() => {
        const analyser = audioContext.createAnalyser();
        // FFT size determines the resolution of the time domain data
        analyser.fftSize = 2048;
        
        sourceNode.connect(analyser);
        analyserRef.current = analyser;

        return () => {
            sourceNode.disconnect(analyser);
            analyser.disconnect();
        };
    }, [audioContext, sourceNode]);

    useEffect(() => {
        const canvas = canvasRef.current;
        const analyser = analyserRef.current;
        if (!canvas || !analyser) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            // Fetch time domain (waveform) data
            analyser.getByteTimeDomainData(dataArray);

            ctx.fillStyle = 'rgb(15, 23, 42)'; // Tailwind slate-900
            ctx.fillRect(0, 0, width, height);

            ctx.lineWidth = lineWidth;
            ctx.strokeStyle = lineColor;
            ctx.beginPath();

            const sliceWidth = (width * 1.0) / bufferLength;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                // Normalize byte to [-1, 1] then map to height
                const v = dataArray[i] / 128.0;
                const y = (v * height) / 2;

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }

                x += sliceWidth;
            }

            ctx.lineTo(width, height / 2);
            ctx.stroke();

            requestRef.current = requestAnimationFrame(draw);
        };

        draw();

        return () => {
            if (requestRef.current) {
                cancelAnimationFrame(requestRef.current);
            }
        };
    }, [width, height, lineColor, lineWidth]);

    return (
        <canvas
            ref={canvasRef}
            width={width}
            height={height}
            className={`rounded-md shadow-inner ${className}`}
            style={{ width: `${width}px`, height: `${height}px` }}
            aria-label="Audio Time-Domain Oscilloscope"
        />
    );
};
