'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CATEGORIES, OMNI_TOOLS, getToolsByCategory } from '@/lib/config';
import { useOmniStore } from '@/lib/store';
import { ToolCategory, OmniTool } from '@/lib/types';
import Link from 'next/link';

// ==========================================
// 🔧 TOOL CARD COMPONENT
// ==========================================
function ToolCard({ tool }: { tool: OmniTool }) {
  const isExecuting = useOmniStore((s) => s.isExecuting);
  const [hovered, setHovered] = useState(false);

  const delegateColors: Record<string, string> = {
    'C++': 'from-blue-500 to-cyan-500',
    'Golang': 'from-cyan-500 to-emerald-500',
    'Python': 'from-yellow-500 to-orange-500',
    'JavaScript': 'from-yellow-400 to-amber-400',
    'C#': 'from-purple-500 to-pink-500',
  };

  const colorClass = delegateColors[tool.delegateTo] || 'from-indigo-500 to-purple-500';

  return (
    <Link href={`/tool/${tool.id}`}>
      <motion.div
        className="group relative glass rounded-xl p-4 cursor-pointer glow-hover"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        {/* Background gradient on hover */}
        <div
          className={`absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-br ${colorClass} -z-10`}
        />

        <div className="relative z-10">
          {/* Icon & Category */}
          <div className="flex items-start justify-between mb-3">
            <span className="text-2xl">{tool.emoji}</span>
            <span className={`text-xs px-2 py-1 rounded-full bg-gradient-to-r ${colorClass} text-white font-medium`}>
              {tool.delegateTo}
            </span>
          </div>

          {/* Name */}
          <h3 className="font-semibold text-white mb-1 group-hover:text-gradient transition-all">
            {tool.name}
          </h3>

          {/* Description */}
          <p className="text-sm text-gray-400 line-clamp-2">
            {tool.description}
          </p>

          {/* Footer */}
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/10">
            <span className="text-xs text-gray-500">{tool.category}</span>
            <span className="text-xs text-gray-500">
              {tool.method === 'POST' ? '📤 POST' : '📥 GET'}
            </span>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}

// ==========================================
// 📊 STATS CARD COMPONENT
// ==========================================
function StatsCard({ emoji, label, count, color }: { emoji: string; label: string; count: number; color: string }) {
  return (
    <motion.div
      className="glass rounded-xl p-4 text-center"
      whileHover={{ scale: 1.05 }}
    >
      <div className={`text-2xl mb-1 ${color}`}>{emoji}</div>
      <div className="text-2xl font-bold text-white">{count}</div>
      <div className="text-xs text-gray-400">{label}</div>
    </motion.div>
  );
}

// ==========================================
// 🏠 MAIN DASHBOARD PAGE
// ==========================================
export default function Dashboard() {
  const [selectedCategory, setSelectedCategory] = useState<ToolCategory | 'ALL'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTools = useMemo(() => {
    return OMNI_TOOLS.filter(tool => {
      const matchCat = selectedCategory === 'ALL' || tool.category === selectedCategory;
      const matchSearch = !searchQuery || 
        tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [selectedCategory, searchQuery]);

  const toolCounts = useMemo(() => {
    const counts: Record<string, number> = { ALL: OMNI_TOOLS.length };
    OMNI_TOOLS.forEach(tool => {
      counts[tool.category] = (counts[tool.category] || 0) + 1;
    });
    return counts;
  }, []);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">⚡</span>
              <div>
                <h1 className="text-xl font-bold text-white">OMNI TOOLS</h1>
                <p className="text-xs text-gray-400">Enterprise Hybrid Platform</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm text-gray-400">Gateway Online</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Category Filter Bar */}
        <div className="mb-6 overflow-x-auto">
          <div className="flex gap-2 pb-2">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id as ToolCategory | 'ALL')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all whitespace-nowrap ${
                  selectedCategory === cat.id
                    ? 'bg-indigo-600 text-white'
                    : 'glass text-gray-300 hover:bg-white/10'
                }`}
              >
                <span>{cat.emoji}</span>
                <span className="font-medium">{cat.label}</span>
                <span className="text-xs bg-black/20 px-2 py-0.5 rounded-full">
                  {toolCounts[cat.id] || 0}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
            <input
              type="text"
              placeholder="Cari tool... (contoh: video, audio, pdf, ai)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 glass rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 mb-8">
          <StatsCard emoji="🌐" label="Total" count={toolCounts.ALL} color="text-white" />
          <StatsCard emoji="🎬" label="Video" count={toolCounts.VIDEO} color="text-blue-400" />
          <StatsCard emoji="🎵" label="Audio" count={toolCounts.AUDIO} color="text-cyan-400" />
          <StatsCard emoji="🖼️" label="Image" count={toolCounts.IMAGE} color="text-green-400" />
          <StatsCard emoji="📄" label="PDF" count={toolCounts.PDF} color="text-red-400" />
          <StatsCard emoji="🔄" label="Converter" count={toolCounts.CONVERTER} color="text-yellow-400" />
          <StatsCard emoji="✨" label="AI" count={toolCounts.AI} color="text-purple-400" />
          <StatsCard emoji="🤖" label="LLM" count={toolCounts.LLM} color="text-pink-400" />
        </div>

        {/* Tools Grid */}
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-white mb-4">
            {selectedCategory === 'ALL' ? 'Semua Tools' : CATEGORIES.find(c => c.id === selectedCategory)?.label}
            <span className="text-gray-400 text-sm font-normal ml-2">({filteredTools.length} tools)</span>
          </h2>
        </div>

        <AnimatePresence mode="wait">
          {filteredTools.length > 0 ? (
            <motion.div
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {filteredTools.map((tool) => (
                <ToolCard key={tool.id} tool={tool} />
              ))}
            </motion.div>
          ) : (
            <motion.div
              className="text-center py-12"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <span className="text-4xl mb-4 block">🔍</span>
              <p className="text-gray-400">Tidak ada tool yang cocok.</p>
              <button
                onClick={() => { setSelectedCategory('ALL'); setSearchQuery(''); }}
                className="mt-4 text-indigo-400 hover:text-indigo-300"
              >
                Lihat semua tools →
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}