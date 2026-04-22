'use client';

import { useState, useEffect, use } from 'react';
import { motion } from 'framer-motion';
import { getToolById } from '@/lib/config';
import { executeTool } from '@/lib/api';
import Link from 'next/link';

// ==========================================
// 🔧 TOOL EXECUTION PAGE
// ==========================================
export default function ToolPage({ params }: { params: { id: string } }) {
  const [file, setFile] = useState<File | null>(null);
  const [params_, setParams] = useState<Record<string, any>>({});
  const [isExecuting, setIsExecuting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const tool = getToolById(params.id);

  useEffect(() => {
    if (!tool) {
      setError('Tool not found');
    }
  }, [tool]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleParamChange = (key: string, value: any) => {
    setParams((prev) => ({ ...prev, [key]: value }));
  };

  const handleExecute = async () => {
    if (!file && !tool?.endpoint.includes('/ai/') && !tool?.endpoint.includes('/llm/')) {
      setError('Silakan pilih file terlebih dahulu');
      return;
    }

    setIsExecuting(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((p) => Math.min(p + Math.random() * 20, 90));
      }, 500);

      // Execute tool via API
      const formData = new FormData();
      if (file) formData.append('file', file);
      
      // Add parameters
      Object.entries(params_).forEach(([key, value]) => {
        formData.append(key, String(value));
      });

      const response = await fetch(tool!.endpoint, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (response.ok) {
        setResult(data);
      } else {
        setError(data.error || 'Execution failed');
      }
    } catch (err: any) {
      setError(err.message || 'Terjadi kesalahan');
    } finally {
      setIsExecuting(false);
    }
  };

  if (!tool) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <span className="text-6xl mb-4 block">🔍</span>
          <h1 className="text-2xl font-bold text-white mb-2">Tool Tidak Ditemukan</h1>
          <p className="text-gray-400 mb-4">Tool ID: {params.id}</p>
          <Link href="/" className="text-indigo-400 hover:text-indigo-300">
            ← Kembali ke Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-white/10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 text-gray-400 hover:text-white">
              <span>←</span>
              <span>Kembali</span>
            </Link>
            
            <div className="flex items-center gap-3">
              <span className="text-2xl">{tool.emoji}</span>
              <div>
                <h1 className="font-semibold text-white">{tool.name}</h1>
                <p className="text-xs text-gray-400">{tool.category} • {tool.delegateTo}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Tool Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-xl p-6 mb-6"
        >
          <h2 className="text-lg font-semibold text-white mb-2">Deskripsi</h2>
          <p className="text-gray-300">{tool.description}</p>
          
          <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-white/10">
            <div>
              <span className="text-xs text-gray-500">Endpoint</span>
              <p className="text-sm text-indigo-400 font-mono">{tool.endpoint}</p>
            </div>
            <div>
              <span className="text-xs text-gray-500">Method</span>
              <p className="text-sm text-white">{tool.method}</p>
            </div>
          </div>
        </motion.div>

        {/* File Upload */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-xl p-6 mb-6"
        >
          <h2 className="text-lg font-semibold text-white mb-4">Input File</h2>
          
          <div className="border-2 border-dashed border-white/20 rounded-lg p-8 text-center hover:border-indigo-500 transition-colors">
            {file ? (
              <div className="flex items-center justify-center gap-3">
                <span className="text-2xl">📄</span>
                <div className="text-left">
                  <p className="text-white font-medium">{file.name}</p>
                  <p className="text-xs text-gray-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="ml-4 text-gray-400 hover:text-red-400"
                >
                  ✕
                </button>
              </div>
            ) : (
              <>
                <span className="text-4xl block mb-2">📁</span>
                <p className="text-gray-400 mb-2">Klik untuk memilih file atau drag & drop</p>
                <p className="text-xs text-gray-500">Maksimal 500MB</p>
                <input
                  type="file"
                  accept={tool.accepts}
                  onChange={handleFileChange}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
              </>
            )}
          </div>
        </motion.div>

        {/* Parameters (if needed) */}
        {/* Note: Add parameter inputs based on tool type */}

        {/* Execute Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <button
            onClick={handleExecute}
            disabled={isExecuting}
            className={`w-full py-4 rounded-xl font-semibold text-lg transition-all ${
              isExecuting
                ? 'bg-gray-600 cursor-not-allowed'
                : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500'
            }`}
          >
            {isExecuting ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin">⚙️</span>
                <span>Memproses...</span>
              </span>
            ) : (
              <span>🚀 Eksekusi Tool</span>
            )}
          </button>

          {/* Progress Bar */}
          {isExecuting && (
            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-400 mb-1">
                <span>Progress</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </motion.div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl"
          >
            <p className="text-red-400">❌ {error}</p>
          </motion.div>
        )}

        {/* Result Display */}
        {result && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 glass rounded-xl p-6"
          >
            <h3 className="text-lg font-semibold text-white mb-4">✅ Hasil</h3>
            <pre className="text-sm text-gray-300 overflow-x-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </motion.div>
        )}
      </main>
    </div>
  );
}