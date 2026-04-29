import React, { useState } from 'react';

interface AudioBlock {
    id: string;
    trackId: number;
    start: number; // in seconds
    duration: number; // in seconds
    label: string;
    color: string;
}

interface TimelineEditorProps {
    totalDuration: number;
    tracksCount: number;
    initialBlocks?: AudioBlock[];
}

export const OmniTimelineEditor: React.FC<TimelineEditorProps> = ({ totalDuration, tracksCount, initialBlocks = [] }) => {
    const [blocks, setBlocks] = useState<AudioBlock[]>(initialBlocks);
    const [playhead, setPlayhead] = useState(0);

    const pixelsPerSecond = 50;

    const handleDragEnd = (id: string, newStart: number) => {
        setBlocks(blocks.map(b => b.id === id ? { ...b, start: Math.max(0, newStart) } : b));
    };

    return (
        <div className="omni-timeline-editor bg-slate-900 border border-slate-700 rounded-xl overflow-hidden shadow-2xl select-none">
            {/* Toolbar */}
            <div className="bg-slate-800 p-4 border-b border-slate-700 flex justify-between items-center">
                <div className="flex gap-4 items-center">
                    <button className="w-10 h-10 rounded-full bg-emerald-500 hover:bg-emerald-400 flex items-center justify-center text-slate-900 transition-colors shadow-lg shadow-emerald-500/20">
                        ▶
                    </button>
                    <button className="w-10 h-10 rounded-full bg-slate-700 hover:bg-slate-600 flex items-center justify-center text-slate-300 transition-colors">
                        ■
                    </button>
                    <div className="font-mono text-emerald-400 font-bold bg-slate-900 px-3 py-1 rounded border border-slate-700">
                        {playhead.toFixed(2)}s / {totalDuration.toFixed(2)}s
                    </div>
                </div>
                <div className="text-sm font-semibold text-sky-400">Omni Audio Composer</div>
            </div>

            {/* Timeline Area */}
            <div className="relative overflow-x-auto min-h-[300px]">
                {/* Time Ruler */}
                <div className="h-8 bg-slate-950 border-b border-slate-800 flex relative" style={{ width: totalDuration * pixelsPerSecond }}>
                    {Array.from({ length: Math.ceil(totalDuration) }).map((_, i) => (
                        <div key={i} className="absolute h-full border-l border-slate-700 pl-1 text-[10px] text-slate-500 font-mono" style={{ left: i * pixelsPerSecond }}>
                            {i}s
                        </div>
                    ))}
                </div>

                {/* Tracks */}
                <div className="relative" style={{ width: totalDuration * pixelsPerSecond }}>
                    {Array.from({ length: tracksCount }).map((_, trackIdx) => (
                        <div key={trackIdx} className="h-24 border-b border-slate-800 relative bg-slate-900/50 hover:bg-slate-800/50 transition-colors">
                            <div className="absolute left-0 top-0 bottom-0 w-16 bg-slate-950 border-r border-slate-800 z-10 flex items-center justify-center text-xs font-bold text-slate-500">
                                TRK {trackIdx + 1}
                            </div>
                            
                            {/* Blocks on this track */}
                            {blocks.filter(b => b.trackId === trackIdx).map(block => (
                                <div 
                                    key={block.id}
                                    className={`absolute top-2 bottom-2 rounded-md border-2 border-white/10 ${block.color} shadow-lg flex flex-col justify-between overflow-hidden cursor-grab active:cursor-grabbing hover:brightness-110 transition-all`}
                                    style={{ 
                                        left: 64 + block.start * pixelsPerSecond, 
                                        width: block.duration * pixelsPerSecond 
                                    }}
                                >
                                    {/* Mock Waveform Texture */}
                                    <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'repeating-linear-gradient(90deg, transparent, transparent 2px, #fff 2px, #fff 4px)' }}></div>
                                    
                                    <div className="px-2 py-1 text-[10px] font-bold text-white/90 truncate relative z-10 drop-shadow-md">
                                        {block.label}
                                    </div>
                                    <div className="px-2 pb-1 text-[9px] font-mono text-white/60 text-right relative z-10">
                                        {block.duration}s
                                    </div>
                                </div>
                            ))}
                        </div>
                    ))}

                    {/* Playhead Marker */}
                    <div className="absolute top-0 bottom-0 w-px bg-rose-500 z-20 pointer-events-none" style={{ left: 64 + playhead * pixelsPerSecond }}>
                        <div className="w-3 h-3 bg-rose-500 rounded-full absolute -left-[5px] -top-1 shadow-[0_0_10px_rgba(244,63,94,0.8)]"></div>
                    </div>
                </div>
            </div>
        </div>
    );
};
