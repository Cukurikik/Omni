import React, { useEffect, useRef } from 'react';

// OMNI INTERFACE LAYER: DL Music Analysis
// Renders the Mel-spectrogram visually using HTML5 Canvas.

interface SpectrogramProps {
  dataUrl: string;
}

export const MusicAnalysisView: React.FC<SpectrogramProps> = ({ dataUrl }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const fetchAndRender = async () => {
      try {
        const res = await fetch(dataUrl);
        const json = await res.json();
        
        if (json.status === 'Ok' && canvasRef.current) {
          const ctx = canvasRef.current.getContext('2d');
          if (!ctx) return;
          
          const specData = json.payload.mel_spectrogram; // 2D array [128][time]
          const width = specData[0].length;
          const height = specData.length;
          
          canvasRef.current.width = width;
          canvasRef.current.height = height;
          
          const imgData = ctx.createImageData(width, height);
          for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
              const val = (specData[y][x] + 80) * 3; // normalized DB to RGB
              const idx = (y * width + x) * 4;
              imgData.data[idx] = val; // R
              imgData.data[idx+1] = val * 0.5; // G
              imgData.data[idx+2] = 255 - val; // B
              imgData.data[idx+3] = 255; // A
            }
          }
          ctx.putImageData(imgData, 0, 0);
        }
      } catch (err) {
        console.error("Failed to render spectrogram", err);
      }
    };
    
    fetchAndRender();
  }, [dataUrl]);

  return (
    <div className="flex flex-col items-center bg-black text-white p-6 rounded-lg shadow-2xl">
      <h2 className="text-2xl font-mono text-purple-400 mb-4">OMNI Spectral Analyzer</h2>
      <div className="border border-purple-900 rounded overflow-hidden">
        <canvas ref={canvasRef} className="w-full max-w-3xl h-64 object-cover" />
      </div>
      <div className="mt-4 flex gap-4 text-sm font-mono text-gray-400">
        <span>FFT Window: 2048</span>
        <span>Hop Length: 512</span>
        <span>Mel Bands: 128</span>
      </div>
    </div>
  );
};
