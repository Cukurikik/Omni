import React, { useState, useEffect } from 'react';

interface TradeLog {
  id: number;
  time: string;
  action: string;
  size: string;
  price: number;
}

export const TradingDesk: React.FC = () => {
  const [balance, setBalance] = useState(100000.0);
  const [drawdown, setDrawdown] = useState(0.02);
  const [logs, setLogs] = useState<TradeLog[]>([]);

  useEffect(() => {
    // Deterministic mock data stream for UI simulation
    const interval = setInterval(() => {
      const isBuy = Math.random() > 0.5;
      const price = 4500 + Math.random() * 50 - 25;
      const newLog: TradeLog = {
        id: Date.now(),
        time: new Date().toLocaleTimeString(),
        action: isBuy ? 'BUY' : 'SELL',
        size: (Math.random() * 5000 + 1000).toFixed(2),
        price: Number(price.toFixed(2))
      };
      
      setLogs(prev => [newLog, ...prev].slice(0, 10));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#0e0e0e] text-green-500 font-mono p-6 min-h-[500px] border border-green-900 rounded">
      <div className="flex justify-between items-center mb-6 border-b border-green-900 pb-2">
        <h1 className="text-xl font-bold uppercase tracking-widest">QuantMuse Terminal</h1>
        <div className="text-right">
          <div>Balance: <span className="text-white">${balance.toFixed(2)}</span></div>
          <div>Drawdown: <span className={drawdown > 0.05 ? 'text-red-500' : 'text-green-500'}>{(drawdown * 100).toFixed(2)}%</span></div>
        </div>
      </div>

      <div className="bg-[#1a1a1a] p-4 rounded mb-4">
        <h2 className="text-sm text-gray-400 mb-2 border-b border-gray-700 pb-1">LIVE EXECUTION LOG</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-500 text-left">
              <th className="pb-2">TIME</th>
              <th className="pb-2">ACTION</th>
              <th className="pb-2">SIZE ($)</th>
              <th className="pb-2">EXEC PRICE</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(l => (
              <tr key={l.id} className="border-t border-gray-800">
                <td className="py-2 text-gray-300">{l.time}</td>
                <td className={`py-2 font-bold ${l.action === 'BUY' ? 'text-blue-400' : 'text-red-400'}`}>{l.action}</td>
                <td className="py-2">{l.size}</td>
                <td className="py-2 text-yellow-400">{l.price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
