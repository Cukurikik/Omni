import React, { useState, useEffect } from 'react';

export const DatasetCatalog: React.FC = () => {
  const [blobs, setBlobs] = useState<{id: string, hash: string, status: string}[]>([]);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      if (t % 3 === 0 && blobs.length < 5) {
        // Deterministic mock hash generation
        const mockHash = Array.from({length: 8}, (_, i) => 
          ((t * 13 + i * 7) % 16).toString(16)
        ).join('') + '...';

        setBlobs(prev => [
          { id: `BLOB_${t}`, hash: mockHash, status: 'INGESTING' },
          ...prev
        ]);
      }

      // Update statuses deterministically
      setBlobs(prev => prev.map(b => {
        if (b.status === 'INGESTING' && Math.random() > 0.5) { // pseudo-deterministic transition
          return { ...b, status: 'INDEXED' };
        }
        return b;
      }));

    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-50 p-6 rounded shadow max-w-lg mx-auto font-sans border border-slate-200">
      <div className="mb-6 flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h2 className="text-xl font-bold text-indigo-600">Diffgram Catalog</h2>
          <p className="text-xs text-slate-500">Blob Ingestion Stream</p>
        </div>
        <div className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded text-xs font-bold shadow-sm">
          {blobs.filter(b => b.status === 'INDEXED').length} BLOBS INDEXED
        </div>
      </div>

      <div className="bg-white rounded border border-slate-200 shadow-inner p-2 min-h-[200px] flex flex-col gap-2">
        {blobs.map(blob => (
          <div key={blob.id} className="flex justify-between items-center p-3 bg-slate-50 border border-slate-100 rounded hover:shadow-sm transition-shadow">
            
            <div className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded flex items-center justify-center text-white text-xs ${blob.status === 'INDEXED' ? 'bg-emerald-500' : 'bg-amber-400 animate-pulse'}`}>
                {blob.status === 'INDEXED' ? '✓' : '⟳'}
              </div>
              <div>
                <div className="text-sm font-bold text-slate-700">{blob.id}</div>
                <div className="text-xs font-mono text-slate-400">{blob.hash}</div>
              </div>
            </div>

            <div className="text-[10px] font-bold tracking-wider px-2 py-1 rounded-full bg-slate-200 text-slate-600">
              {blob.status}
            </div>
            
          </div>
        ))}
        {blobs.length === 0 && (
          <div className="m-auto text-slate-400 text-sm">Awaiting stream...</div>
        )}
      </div>
    </div>
  );
};
