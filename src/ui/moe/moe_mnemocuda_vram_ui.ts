// moe_mnemocuda_vram_ui.ts — Interface Layer: MnemoCUDA VRAM UI
// TypeScript React component rendering VRAM vs NVMe tiering memory bars.

import React from 'react';

interface MemoryProps {
  vramUsedMb: number;
  vramTotalMb: number;
  nvmeUsedMb: number;
}

export const MemoryTierBar: React.FC<MemoryProps> = ({ vramUsedMb, vramTotalMb, nvmeUsedMb }) => {
  const vramPercent = Math.min((vramUsedMb / vramTotalMb) * 100, 100);

  return React.createElement('div', { className: 'memory-container', style: { width: '100%', padding: '10px' } },
    React.createElement('h4', null, `GPU VRAM: ${vramUsedMb}MB / ${vramTotalMb}MB`),
    React.createElement('div', { style: { width: '100%', height: '20px', background: '#333', borderRadius: '4px' } },
      React.createElement('div', { style: { width: `${vramPercent}%`, height: '100%', background: vramPercent > 90 ? '#ff4444' : '#44ff44', borderRadius: '4px' } })
    ),
    React.createElement('h4', { style: { marginTop: '10px' } }, `NVMe Swap (Direct Storage): ${nvmeUsedMb}MB`)
  );
};
