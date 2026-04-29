import React, { useState, useEffect } from 'react';

export const InsightDashboard: React.FC = () => {
  const [docs, setDocs] = useState([
    { name: "Q3_Financials.pdf", status: 100, insights: 14 },
    { name: "Employee_Handbook.docx", status: 100, insights: 42 },
    { name: "Project_Apollo_Specs.pdf", status: 45, insights: 0 }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setDocs(prev => prev.map(doc => {
        if (doc.status < 100) {
          const newStatus = Math.min(100, doc.status + 5);
          return { ...doc, status: newStatus, insights: newStatus === 100 ? 8 : 0 };
        }
        return doc;
      }));
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">FileWise</h2>
          <p className="text-xs text-slate-400">Document Insight Pipeline</p>
        </div>
        <div className="text-sky-500 bg-sky-900/30 px-2 py-1 rounded text-xs font-bold border border-sky-800">
          RAG ACTIVE
        </div>
      </div>

      <div className="space-y-4">
        {docs.map((doc, i) => (
          <div key={i} className="bg-slate-800 p-3 rounded border border-slate-700">
            <div className="flex justify-between items-center mb-2">
              <span className="font-mono text-sm text-white truncate w-40">{doc.name}</span>
              <span className="text-xs font-bold text-sky-300">{doc.insights > 0 ? `${doc.insights} Insights` : 'Parsing...'}</span>
            </div>
            <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
              <div 
                className={`h-full ${doc.status === 100 ? 'bg-sky-500' : 'bg-sky-400 animate-pulse'}`} 
                style={{ width: `${doc.status}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
