import React, { useEffect, useRef } from 'react';

// OmniAudioVisualizer.tsx — Web Audio API Visualizer
// Layer: Interface / TypeScript
//
// Hooks into the browser's Web Audio API AnalyserNode to render
// a real-time frequency bar graph on an HTML5 Canvas. Zero mock.

export interface OmniAudioVisualizerProps {
    audioContext: AudioContext;
    sourceNode: AudioNode;
    width: number;
    height: number;
    barColor?: string;
    className?: string;
}

export const OmniAudioVisualizer: React.FC<OmniAudioVisualizerProps> = ({
    audioContext,
    sourceNode,
    width,
    height,
    barColor = '#3b82f6', // Tailwind blue-500
    className = ''
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const requestRef = useRef<number>();
    const analyserRef = useRef<AnalyserNode | null>(null);

    useEffect(() => {
        // Setup Web Audio Analyser
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256; // Defines the number of frequency bins (128)
        
        // Connect the source through the analyser
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
            // Get frequency data
            analyser.getByteFrequencyData(dataArray);

            // Clear canvas
            ctx.clearRect(0, 0, width, height);

            const barWidth = (width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                barHeight = dataArray[i];

                // Normalize height relative to canvas
                const scaledHeight = (barHeight / 255) * height;

                ctx.fillStyle = barColor;
                // Draw bar from bottom up
                ctx.fillRect(x, height - scaledHeight, barWidth, scaledHeight);

                x += barWidth + 1;
            }

            requestRef.current = requestAnimationFrame(draw);
        };

        draw();

        return () => {
            if (requestRef.current) {
                cancelAnimationFrame(requestRef.current);
            }
        };
    }, [width, height, barColor]);

    return (
        <canvas
            ref={canvasRef}
            width={width}
            height={height}
            className={`rounded-md bg-slate-900 ${className}`}
            style={{ width: `${width}px`, height: `${height}px` }}
            aria-label="Audio Frequency Visualizer"
        />
    );
};
