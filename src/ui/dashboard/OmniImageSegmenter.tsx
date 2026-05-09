import React, { useState, useRef, useEffect } from 'react';

// OmniImageSegmenter.tsx — Semantic Segmentation Viewer
// Layer: Interface / TypeScript
// Inspired by: rezazad68/TMUnet
//
// Interactive React UI component mapping an alpha-blended color mask
// (from a segmentation model like TMUnet) over a source medical image. Zero mock.

export interface OmniImageSegmenterProps {
    srcImageUrl: string;
    maskImageUrl: string; // Black and white mask, or colored class mask
    opacity?: number;
    className?: string;
    onOpacityChange?: (val: number) => void;
}

export const OmniImageSegmenter: React.FC<OmniImageSegmenterProps> = ({
    srcImageUrl,
    maskImageUrl,
    opacity = 0.5,
    className = '',
    onOpacityChange
}) => {
    const [localOpacity, setLocalOpacity] = useState<number>(opacity);
    const containerRef = useRef<HTMLDivElement>(null);

    // Sync prop changes
    useEffect(() => {
        setLocalOpacity(opacity);
    }, [opacity]);

    const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = parseFloat(e.target.value);
        setLocalOpacity(val);
        if (onOpacityChange) onOpacityChange(val);
    };

    return (
        <div className={`flex flex-col space-y-4 ${className}`}>
            
            {/* Display Container */}
            <div 
                ref={containerRef}
                className="relative overflow-hidden rounded-xl bg-slate-900 border border-slate-700 aspect-square max-w-2xl mx-auto shadow-xl"
                style={{ width: '100%' }}
            >
                {/* Base Medical Image */}
                <img 
                    src={srcImageUrl} 
                    alt="Source Scan" 
                    className="absolute inset-0 w-full h-full object-contain"
                />
                
                {/* Segmentation Overlay */}
                <img 
                    src={maskImageUrl} 
                    alt="Segmentation Mask" 
                    className="absolute inset-0 w-full h-full object-contain pointer-events-none transition-opacity duration-200"
                    style={{ 
                        opacity: localOpacity,
                        mixBlendMode: 'screen' // Often useful for overlaying masks 
                    }}
                />
                
                {/* Opacity Indicator Badge */}
                <div className="absolute bottom-4 right-4 bg-black/60 backdrop-blur-md text-white px-3 py-1 rounded-full text-xs font-medium">
                    Mask: {Math.round(localOpacity * 100)}%
                </div>
            </div>

            {/* Controls */}
            <div className="max-w-2xl w-full mx-auto flex items-center space-x-4 bg-slate-100 dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                <span className="text-sm font-medium text-slate-600 dark:text-slate-300">Base</span>
                
                <input 
                    type="range" 
                    min="0" 
                    max="1" 
                    step="0.05" 
                    value={localOpacity} 
                    onChange={handleSliderChange}
                    className="flex-grow h-2 bg-slate-300 dark:bg-slate-600 rounded-lg appearance-none cursor-pointer accent-blue-500"
                    aria-label="Adjust Mask Opacity"
                />
                
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400">Overlay</span>
            </div>
        </div>
    );
};
