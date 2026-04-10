import React, { useState } from 'react';
import { useOmniJob } from '../hooks/useOmniJob'; // Hook WebSocket Anti-Badai kita

export default function AiVisionTool() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  
  // OMNI-SYNC: Memantau Python & Golang secara Real-time!
  const { status, progress, message } = useOmniJob(jobId);

  const handleExecute = async () => {
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);

    // Kirim gambar ke Golang (Pipa Utama)
    const res = await fetch('/api/v1/omni/execute?tool_id=ai_vision', {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    setJobId(data.data.job_id); // Kunci target, WebSocket akan otomatis menyala!
  };

  return (
    <div className="p-8 max-w-2xl mx-auto bg-gray-900 text-white rounded-xl shadow-2xl border border-gray-700">
      <h2 className="text-3xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
        AI Vision Edge Detector
      </h2>
      <p className="text-gray-400 mb-6">Ditenagai oleh Python OpenCV di dalam Jantung Golang.</p>

      <input 
        type="file" 
        accept="image/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 mb-4 cursor-pointer"
      />

      <button 
        onClick={handleExecute}
        disabled={!file || status === 'PROCESSING'}
        className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold py-3 rounded shadow hover:scale-[1.02] transition-transform disabled:opacity-50"
      >
        {status === 'PROCESSING' ? `Memproses AI... ${progress}%` : 'Eksekusi Gambar'}
      </button>

      {/* Tampilan Hasil Spek Dewa */}
      {status === 'COMPLETED' && (
        <div className="mt-6 p-4 bg-gray-800 rounded border border-green-500">
          <p className="text-green-400 font-bold mb-2">✅ Analisis Selesai: {message}</p>
          <a 
            href={`/api/v1/omni/download?job_id=${jobId}`} 
            className="text-blue-400 underline hover:text-blue-300"
            download
          >
            👇 Unduh Hasil Sketsa AI
          </a>
        </div>
      )}
    </div>
  );
}
