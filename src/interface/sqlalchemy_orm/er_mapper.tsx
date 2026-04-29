import React, { useState, useEffect } from 'react';

export const ERMapper: React.FC = () => {
  const [queries, setQueries] = useState<{id: string, table: string, cost: number}[]>([]);

  useEffect(() => {
    let qId = 0;
    const interval = setInterval(() => {
      qId++;
      const tables = ['users', 'orders', 'products', 'inventory'];
      const table = tables[qId % tables.length];
      
      // Simulated deterministic cardinality/cost
      const cost = Math.floor(Math.random() * 500) + 10;

      setQueries(prev => {
        const next = [{ id: `Q_${qId.toString().padStart(4, '0')}`, table, cost }, ...prev];
        return next.slice(0, 6);
      });
    }, 600);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-50 p-6 rounded-lg border border-slate-200 shadow-xl max-w-sm mx-auto font-sans">
      <div className="mb-6 border-b border-slate-200 pb-2 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-sky-700">SQLAlchemy ORM</h2>
          <p className="text-xs text-slate-500">Live Query Execution Monitor</p>
        </div>
        <div className="flex gap-1">
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce"></div>
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {queries.map(q => (
          <div key={q.id} className="bg-white p-3 rounded border border-slate-200 flex justify-between items-center shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded bg-sky-100 flex items-center justify-center text-sky-600">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path>
                </svg>
              </div>
              <div>
                <div className="font-bold text-sm text-slate-700">{q.table}</div>
                <div className="text-[10px] text-slate-400 font-mono">ID: {q.id}</div>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-[10px] font-bold text-slate-400 uppercase">Cost</div>
              <div className={`text-sm font-mono font-bold ${q.cost > 300 ? 'text-rose-500' : 'text-emerald-500'}`}>
                {q.cost}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
