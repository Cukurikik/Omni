import React, { useState, useEffect } from 'react';

export const FeatureRegistry: React.FC = () => {
  const [featureViews, setFeatureViews] = useState<{name: string, entities: string[], ttl: number, status: string}[]>([]);

  useEffect(() => {
    // Deterministic population of Feast Feature Views
    const initial = [
      { name: 'user_transaction_counts_7d', entities: ['user_id'], ttl: 604800, status: 'SYNCING' },
      { name: 'merchant_fraud_rate_1d', entities: ['merchant_id'], ttl: 86400, status: 'SYNCING' },
      { name: 'driver_hourly_stats', entities: ['driver_id'], ttl: 3600, status: 'SYNCING' }
    ];
    setFeatureViews(initial);

    const interval = setInterval(() => {
      setFeatureViews(prev => prev.map(fv => {
        if (fv.status === 'SYNCING') {
          return { ...fv, status: Math.random() > 0.5 ? 'ONLINE' : 'SYNCING' };
        }
        return fv;
      }));
    }, 800);

    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (status: string) => {
    if (status === 'ONLINE') return <span className="bg-emerald-100 text-emerald-700 px-2 py-1 text-[10px] font-bold rounded">ONLINE</span>;
    return <span className="bg-amber-100 text-amber-700 px-2 py-1 text-[10px] font-bold rounded animate-pulse">SYNCING</span>;
  };

  return (
    <div className="bg-slate-50 p-6 rounded border border-slate-200 shadow-xl max-w-2xl mx-auto font-sans">
      <div className="mb-6 border-b border-slate-200 pb-4 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-rose-600">Feast Feature Registry</h2>
          <p className="text-xs text-slate-500">Materialized Online Store Views</p>
        </div>
        <div className="text-xs font-mono bg-white px-3 py-1 rounded shadow-sm border border-slate-200 text-slate-600">
          Redis: CONNECTED
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {featureViews.map((fv, i) => (
          <div key={i} className="bg-white p-4 rounded border border-slate-200 shadow-sm flex items-center justify-between hover:shadow-md transition-shadow">
            <div>
              <div className="font-bold text-slate-800 text-sm mb-1">{fv.name}</div>
              <div className="flex gap-2 text-xs text-slate-500 font-mono">
                <span>Entities: [{fv.entities.join(', ')}]</span>
                <span>•</span>
                <span>TTL: {fv.ttl}s</span>
              </div>
            </div>
            <div>
              {getStatusBadge(fv.status)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
