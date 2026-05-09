import React, { useEffect, useRef } from 'react';

// OmniSpectrogram.tsx — Web Audio API Waterfall Spectrogram
// Layer: Interface / TypeScript
//
// Hooks into the browser's Web Audio API AnalyserNode to render
// a continuous frequency waterfall graph over time (Spectrogram). Zero mock.

export interface OmniSpectrogramProps {
    audioContext: AudioContext;
    sourceNode: AudioNode;
    width: number;
    height: number;
    className?: string;
    speed?: number; // Pixels to scroll per frame
}

export const OmniSpectrogram: React.FC<OmniSpectrogramProps> = ({
    audioContext,
    sourceNode,
    width,
    height,
    className = '',
    speed = 1
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const requestRef = useRef<number>();
    const analyserRef = useRef<AnalyserNode | null>(null);
    
    // An offscreen canvas is used to scroll the image smoothly
    const tempCanvasRef = useRef<HTMLCanvasElement | null>(null);

    useEffect(() => {
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 512; // Controls vertical resolution
        analyser.smoothingTimeConstant = 0.0; // Raw immediate data
        
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

        const ctx = canvas.getContext('2d', { alpha: false });
        if (!ctx) return;

        // Initialize temp canvas for scrolling buffer
        if (!tempCanvasRef.current) {
            const temp = document.createElement('canvas');
            temp.width = width;
            temp.height = height;
            const tempCtx = temp.getContext('2d', { alpha: false });
            if (tempCtx) {
                tempCtx.fillStyle = 'rgb(0,0,0)';
                tempCtx.fillRect(0, 0, width, height);
            }
            tempCanvasRef.current = temp;
        }
        const tempCtx = tempCanvasRef.current.getContext('2d');
        if (!tempCtx) return;

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        // Simple colormap generator (black -> purple -> orange -> yellow -> white)
        const getStyle = (value: number) => {
            const ratio = value / 255;
            const r = Math.floor(Math.max(0, Math.min(255, ratio * 2.5 * 255)));
            const g = Math.floor(Math.max(0, Math.min(255, (ratio - 0.3) * 3 * 255)));
            const b = Math.floor(Math.max(0, Math.min(255, (1 - Math.abs(ratio - 0.5)*2) * 255)));
            return `rgb(${r},${g},${b})`;
        };

        const draw = () => {
            analyser.getByteFrequencyData(dataArray);

            // Shift temp canvas left by `speed` pixels
            tempCtx.drawImage(tempCanvasRef.current!, speed, 0, width - speed, height, 0, 0, width - speed, height);

            // Draw new column of frequency data on the far right
            const binHeight = height / bufferLength;
            for (let i = 0; i < bufferLength; i++) {
                tempCtx.fillStyle = getStyle(dataArray[i]);
                // Frequencies are low at index 0, so we draw from bottom to top
                tempCtx.fillRect(width - speed, height - (i * binHeight) - binHeight, speed, Math.ceil(binHeight));
            }

            // Blit temp canvas to visible canvas
            ctx.drawImage(tempCanvasRef.current!, 0, 0);

            requestRef.current = requestAnimationFrame(draw);
        };

        draw();

        return () => {
            if (requestRef.current) {
                cancelAnimationFrame(requestRef.current);
            }
        };
    }, [width, height, speed]);

    return (
        <canvas
            ref={canvasRef}
            width={width}
            height={height}
            className={`rounded-md shadow-lg ${className}`}
            style={{ width: `${width}px`, height: `${height}px` }}
            aria-label="Audio Spectral Waterfall"
        />
    );
};
