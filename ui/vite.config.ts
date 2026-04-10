import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// ==========================================
// ⚡ OMNI-VITE: FULL-STACK PROXY ENGINE
// ==========================================
// Strategi Diplomasi: Merangkul Vite (standar industri)
// sambil mempertahankan Golang Bare-Metal sebagai Backend.
//
// PORT MAP:
//   🖥️  Vite Dev Server   → http://localhost:5173 (Frontend HMR)
//   🐹 Golang Gateway     → http://localhost:3000 (Backend API)
//   📡 WebSocket Proxy    → ws://localhost:3000/ws/* (Live Sync)
// ==========================================
export default defineConfig({
  plugins: [react()],

  // Root points to src/ where index.html lives
  root: 'src',

  // Path aliases — mirip dengan tsconfig paths
  resolve: {
    alias: {
      '@omni': path.resolve(__dirname, 'src/omni'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@pages': path.resolve(__dirname, 'src/pages'),
      '@configs': path.resolve(__dirname, 'src/configs'),
    },
  },

  server: {
    port: 5173,
    strictPort: true,
    // Buka akses dari perangkat LAN (HP, tablet)
    host: true,

    proxy: {
      // ━━━ REST API PROXY ━━━
      // Semua /api/* → Golang Gateway (Zero CORS!)
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        secure: false,
      },

      // ━━━ WEBSOCKET PROXY ━━━
      // OMNI-SYNC Progress Bar + Live Job Updates
      '/ws': {
        target: 'http://localhost:3000',
        ws: true,
        changeOrigin: true,
      },
    },
  },

  // Production build → release/public/ (untuk Golang serve)
  build: {
    outDir: '../../release/public',
    emptyOutDir: true,
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          motion: ['framer-motion'],
        },
      },
    },
  },

  // COOP/COEP headers untuk SharedArrayBuffer (WASM/WebGPU)
  optimizeDeps: {
    include: ['react', 'react-dom', 'framer-motion'],
  },
});
