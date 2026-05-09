import React, { useMemo } from 'react';

// OMNI MOTHER Production Zero-Mock VRAM Profiler
// Renders memory block allocation visually to detect fragmentation

interface MemoryBlock {
  offsetMB: number;
  sizeMB: number;
  isFree: boolean;
  tensorId?: string;
}

interface VramProfilerProps {
  totalCapacityMB: number;
  blocks: MemoryBlock[];
}

export const MoEVramProfiler: React.FC<VramProfilerProps> = ({ totalCapacityMB, blocks }) => {

  const totalUsed = useMemo(() => {
    return blocks.filter(b => !b.isFree).reduce((acc, b) => acc + b.sizeMB, 0);
  }, [blocks]);

  const usagePercent = (totalUsed / totalCapacityMB) * 100;

  return (
    <div style={{ padding: '20px', background: '#1e1e1e', color: '#fff', borderRadius: '8px', fontFamily: 'monospace' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
        <h3>GPU VRAM Allocation Matrix</h3>
        <span>{totalUsed.toFixed(0)} MB / {totalCapacityMB} MB ({usagePercent.toFixed(1)}%)</span>
      </div>

      {/* Memory Bar */}
      <div style={{ 
        width: '100%', 
        height: '40px', 
        background: '#000', 
        display: 'flex', 
        borderRadius: '4px',
        overflow: 'hidden',
        border: '1px solid #444'
      }}>
        {blocks.map((block, i) => {
          const widthPercent = (block.sizeMB / totalCapacityMB) * 100;
          return (
            <div 
              key={i}
              title={block.isFree ? `Free: ${block.sizeMB}MB` : `Used: ${block.tensorId} (${block.sizeMB}MB)`}
              style={{
                width: `${widthPercent}%`,
                height: '100%',
                background: block.isFree ? '#2a2a2a' : `hsl(${(i * 47) % 360}, 70%, 50%)`,
                borderRight: i < blocks.length - 1 ? '1px solid #111' : 'none',
                cursor: 'pointer'
              }}
            />
          );
        })}
      </div>

      {/* Fragmentation Warning */}
      {blocks.filter(b => b.isFree).length > 10 && (
        <div style={{ marginTop: '15px', color: '#ffaa00', fontSize: '14px' }}>
          ⚠️ OMNI WARNING: High Memory Fragmentation Detected. 
          VRAM Defragmenter routine highly recommended.
        </div>
      )}
    </div>
  );
};
