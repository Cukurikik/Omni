import React, { useState, useEffect } from 'react';

// OMNI INTERFACE LAYER: Reproducibility Report
// Renders the health and score of research repositories.

interface RepoReport {
  url: string;
  score: number;
  grade: 'A' | 'B' | 'C' | 'F';
  deductions: string[];
}

export const ReproducibilityReport: React.FC = () => {
  const [reports, setReports] = useState<RepoReport[]>([]);

  useEffect(() => {
    fetch('/api/omni/reproducibility/reports')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'Ok') setReports(data.payload);
      })
      .catch(err => console.error("OmniBridge Error:", err));
  }, []);

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'text-green-500 bg-green-900/30 border-green-500';
      case 'B': return 'text-yellow-500 bg-yellow-900/30 border-yellow-500';
      case 'C': return 'text-orange-500 bg-orange-900/30 border-orange-500';
      default: return 'text-red-500 bg-red-900/30 border-red-500';
    }
  };

  return (
    <div className="p-8 bg-[#f8fafc] min-h-screen text-slate-900 font-sans">
      <h1 className="text-3xl font-bold text-slate-800 mb-2">Omni Research Reproducibility Index</h1>
      <p className="text-slate-500 mb-8 max-w-2xl">Automated structural analysis based on NeurIPS ML Code completeness guidelines.</p>
      
      <div className="grid gap-6 max-w-4xl">
        {reports.length === 0 ? (
          <div className="p-6 bg-white border border-slate-200 rounded shadow-sm animate-pulse">
            Scanning repositories via Rust FFI AST parser...
          </div>
        ) : (
          reports.map((repo, idx) => (
            <div key={idx} className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 flex gap-6 items-start hover:shadow-md transition-shadow">
              <div className={`w-16 h-16 rounded-full border-2 flex items-center justify-center text-3xl font-black ${getGradeColor(repo.grade)}`}>
                {repo.grade}
              </div>
              
              <div className="flex-1">
                <h3 className="text-lg font-bold text-blue-600 truncate">{repo.url}</h3>
                <div className="flex items-center gap-2 mt-1 mb-4 text-sm text-slate-500 font-mono">
                  <span>Score: <span className="font-bold text-slate-700">{repo.score}/100</span></span>
                </div>
                
                {repo.deductions.length > 0 && (
                  <div className="bg-red-50 rounded-lg p-3">
                    <h4 className="text-xs font-bold text-red-800 uppercase tracking-wider mb-2">Deductions</h4>
                    <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
                      {repo.deductions.map((deduction, i) => (
                        <li key={i}>{deduction}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
