// omni_layout.tsx — Main Dashboard Layout Shell
// Layer: UI / TypeScript & React
//
// Provides the structural navigation, sidebar, and routing container
// for the OMNI operations dashboard using modern React patterns.

import React, { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export const OmniDashboardLayout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-900 text-gray-100 overflow-hidden font-sans">
      
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col shadow-2xl z-10">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            OMNI NEXUS
          </h2>
          <p className="text-xs text-gray-500 mt-1 uppercase tracking-widest font-mono">Operations Console</p>
        </div>
        
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <NavItem icon="📊" label="System Metrics" active />
          <NavItem icon="🤖" label="Model Registry" />
          <NavItem icon="⚡" label="Active Inferences" />
          <NavItem icon="🧠" label="Memory Pools (VRAM)" />
          <NavItem icon="🌐" label="Network Topology" />
          <NavItem icon="🛡️" label="Security & Access" />
        </nav>
        
        <div className="p-4 border-t border-gray-700 text-xs text-gray-500 font-mono">
          <p>Version: 3.0.0-MOTHER</p>
          <p>Status: <span className="text-green-400">All Systems Nominal</span></p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Top Header */}
        <header className="h-16 bg-gray-800/80 backdrop-blur-md border-b border-gray-700 flex items-center justify-between px-6 z-10">
          <div className="text-sm font-medium text-gray-400">
            Path: /dashboard/metrics
          </div>
          <div className="flex items-center gap-4">
            <button className="omni-button text-sm py-1.5 px-4">
              Deploy Update
            </button>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold shadow-lg shadow-purple-500/20">
              A
            </div>
          </div>
        </header>

        {/* Scrollable Workspace */}
        <div className="flex-1 overflow-auto p-6 relative">
          {/* Background decoration */}
          <div className="absolute top-0 left-0 w-full h-96 bg-gradient-to-b from-blue-900/10 to-transparent pointer-events-none" />
          <div className="relative z-10">
            {children}
          </div>
        </div>
      </main>

    </div>
  );
};

const NavItem: React.FC<{ icon: string; label: string; active?: boolean }> = ({ icon, label, active }) => (
  <button 
    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors duration-200 ${
      active 
        ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-[inset_0_0_12px_rgba(59,130,246,0.1)]' 
        : 'text-gray-400 hover:bg-gray-700/50 hover:text-gray-200'
    }`}
  >
    <span className="text-lg">{icon}</span>
    <span className="font-medium text-sm">{label}</span>
  </button>
);
