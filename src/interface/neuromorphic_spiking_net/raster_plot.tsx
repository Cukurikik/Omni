import React, { useState, useEffect } from 'react';

export const RasterPlot: React.FC = () => {
  const [spikes, setSpikes] = useState<{id: number, neuron: number, time: number}[]>([]);
  const [time, setTime] = useState(0);
  const numNeurons = 20;

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(t => {
         const newT = t + 1;
         
         // Generate random spikes (simulating network activity)
         const newSpikes = [];
         for(let i = 0; i < numNeurons; i++) {
            // 5% chance to spike per tick per neuron
            if (Math.random() < 0.05) {
               newSpikes.push({ id: Math.random(), neuron: i, time: newT });
            }
         }
         
         setSpikes(prev => [...prev.filter(s => newT - s.time < 50), ...newSpikes]);
         return newT;
      });
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-amber-500">Spiking Net</h2>
          <p className="text-xs text-slate-400">Neuromorphic Raster Plot</p>
        </div>
        <div className="px-2 py-1 bg-amber-900/30 text-amber-500 text-[10px] font-mono rounded border border-amber-800">
          Intel Loihi Sim
        </div>
      </div>

      <div className="bg-slate-950 p-2 rounded border border-slate-800 h-[200px] relative overflow-hidden mb-4">
         
         {/* Y-Axis labels (Neuron ID) */}
         <div className="absolute left-0 top-0 bottom-0 w-6 flex flex-col justify-between items-center text-[6px] text-slate-600 py-2 border-r border-slate-800 bg-slate-900 z-20">
            <span>{numNeurons}</span>
            <span>{numNeurons/2}</span>
            <span>0</span>
         </div>

         {/* Plot Area */}
         <div className="absolute left-6 right-0 top-0 bottom-0">
            {spikes.map(s => {
               // Calculate X position based on time window (last 50 ticks)
               const xPos = 100 - ((time - s.time) / 50) * 100;
               // Calculate Y position based on neuron ID
               const yPos = (s.neuron / numNeurons) * 100;
               
               return (
                 <div 
                   key={s.id}
                   className="absolute w-1 h-1 bg-amber-500 rounded-full shadow-[0_0_5px_#f59e0b]"
                   style={{ left: `${xPos}%`, top: `${yPos}%` }}
                 ></div>
               );
            })}
            
            {/* Playhead Scanner */}
            <div className="absolute top-0 bottom-0 right-0 w-px bg-white/20 shadow-[0_0_10px_white]"></div>
         </div>
      </div>
      
      <div className="flex justify-between text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Tick: {time} ms</span>
         <span>Spike Rate: {(spikes.length / (numNeurons * 0.05)).toFixed(1)} Hz</span>
         <span>Power: <span className="text-emerald-400">12 mW</span></span>
      </div>
    </div>
  );
};
