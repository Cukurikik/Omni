// ⚡ OMNI TOOLS — React Entry Point
// Vite handles HMR injection automatically via @vitejs/plugin-react

import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './styles.css'; // Vite imports CSS sebagai module — auto HMR!

// 🎨 OMNI-CANVAS: Dynamic Styling Injection
declare global {
    interface Window {
        __OMNI_CONFIG__?: {
            ui_engine?: {
                css_framework?: string;
                inject_css_path?: string;
            }
        };
    }
}

const injectStyles = () => {
    // Abaikan jika tidak ada config (misal saat dev tanpa CLI)
    if (typeof window !== 'undefined' && window.__OMNI_CONFIG__?.ui_engine) {
        const uiConfig = window.__OMNI_CONFIG__.ui_engine;
        
        if (uiConfig.css_framework === 'tailwind') {
            // Tailwind sudah di-import via styles.css biasanya, tapi kita bisa load spesifik
            // import('./styles/tailwind.css'); 
        } else if (uiConfig.css_framework === 'bootstrap') {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css';
            document.head.appendChild(link);
        }
        
        // Injeksi file CSS Custom militer (Kedaulatan Penuh)
        if (uiConfig.inject_css_path) {
            const customLink = document.createElement('link');
            customLink.rel = 'stylesheet';
            customLink.href = uiConfig.inject_css_path;
            document.head.appendChild(customLink);
        }
    }
};

injectStyles();

const container = document.getElementById('root');
if (container) {
    const root = createRoot(container);
    root.render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    );
}
