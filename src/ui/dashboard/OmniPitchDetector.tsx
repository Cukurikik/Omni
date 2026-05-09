import React, { useEffect, useRef, useState } from 'react';

// OmniPitchDetector.tsx — YIN Pitch Detection
// Layer: Interface / TypeScript / Compute
//
// Implements the YIN fundamental frequency estimator algorithm in JavaScript.
// Processes microphone audio to detect the musical pitch (Hz) in real-time.
// Zero mock algorithm structure.

export interface OmniPitchDetectorProps {
    audioContext: AudioContext;
    sourceNode: AudioNode;
    className?: string;
}

export const OmniPitchDetector: React.FC<OmniPitchDetectorProps> = ({
    audioContext,
    sourceNode,
    className = ''
}) => {
    const [pitch, setPitch] = useState<number>(0);
    const requestRef = useRef<number>();
    const analyserRef = useRef<AnalyserNode | null>(null);

    useEffect(() => {
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048; // Buffer size (W)
        
        sourceNode.connect(analyser);
        analyserRef.current = analyser;

        return () => {
            sourceNode.disconnect(analyser);
            analyser.disconnect();
        };
    }, [audioContext, sourceNode]);

    useEffect(() => {
        const analyser = analyserRef.current;
        if (!analyser) return;

        const bufferLength = analyser.fftSize;
        const dataArray = new Float32Array(bufferLength);
        const sampleRate = audioContext.sampleRate;

        // YIN algorithm buffers
        const halfBufferSize = bufferLength / 2;
        const yinBuffer = new Float32Array(halfBufferSize);

        const detectPitch = () => {
            analyser.getFloatTimeDomainData(dataArray);

            // Step 1: Calculate the difference function
            for (let tau = 0; tau < halfBufferSize; tau++) {
                yinBuffer[tau] = 0;
            }
            for (let tau = 1; tau < halfBufferSize; tau++) {
                for (let i = 0; i < halfBufferSize; i++) {
                    const delta = dataArray[i] - dataArray[i + tau];
                    yinBuffer[tau] += delta * delta;
                }
            }

            // Step 2: Cumulative mean normalized difference function
            let runningSum = 0;
            yinBuffer[0] = 1;
            for (let tau = 1; tau < halfBufferSize; tau++) {
                runningSum += yinBuffer[tau];
                yinBuffer[tau] *= tau / runningSum;
            }

            // Step 3: Absolute threshold
            let tauEstimate = -1;
            const THRESHOLD = 0.1;
            for (let tau = 2; tau < halfBufferSize; tau++) {
                if (yinBuffer[tau] < THRESHOLD) {
                    while (tau + 1 < halfBufferSize && yinBuffer[tau + 1] < yinBuffer[tau]) {
                        tau++;
                    }
                    tauEstimate = tau;
                    break;
                }
            }

            // Step 4: Parabolic interpolation
            if (tauEstimate !== -1) {
                const x0 = tauEstimate - 1;
                const x2 = tauEstimate + 1;
                if (x0 >= 0 && x2 < halfBufferSize) {
                    const s0 = yinBuffer[x0];
                    const s1 = yinBuffer[tauEstimate];
                    const s2 = yinBuffer[x2];
                    
                    const shift = 0.5 * (s2 - s0) / (2 * s1 - s2 - s0);
                    const exactTau = tauEstimate + shift;
                    
                    const freq = sampleRate / exactTau;
                    setPitch(freq);
                }
            } else {
                setPitch(0); // No pitch detected
            }

            requestRef.current = requestAnimationFrame(detectPitch);
        };

        detectPitch();

        return () => {
            if (requestRef.current) {
                cancelAnimationFrame(requestRef.current);
            }
        };
    }, [audioContext]);

    // Format output
    let note = "-";
    if (pitch > 0) {
        // A4 = 440Hz
        const notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
        const pitchMidi = Math.round(69 + 12 * Math.log2(pitch / 440.0));
        note = `${notes[pitchMidi % 12]}${Math.floor(pitchMidi / 12) - 1}`;
    }

    return (
        <div className={`p-6 bg-slate-800 rounded-xl flex flex-col items-center justify-center shadow-lg ${className}`}>
            <h3 className="text-slate-400 text-sm uppercase tracking-widest mb-2">Live Pitch</h3>
            <div className="text-5xl font-mono text-emerald-400 font-bold tracking-tighter">
                {pitch > 0 ? pitch.toFixed(1) : '---'} <span className="text-2xl text-emerald-600/50">Hz</span>
            </div>
            <div className="mt-4 text-2xl font-bold text-slate-200">
                {note}
            </div>
        </div>
    );
};
