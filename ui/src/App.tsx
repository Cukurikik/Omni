// ==========================================
// ⚡ OMNI APP — Entry Point
// ==========================================
// Framework: OMNI (C++ · Golang · Python · TypeScript)
// Router: OMNI-NAVIGATOR (custom hash-based SPA router)
// Client: OMNI-CLIENT (native HTTP/WebSocket SDK)
// SSR: OMNI-RENDER ENGINE (Golang injects SEO + Hydration State)

import React, { useEffect } from 'react';
import { OmniRouter, OmniRoutes, hasOmniSSR } from './omni';
import type { OmniRoute } from './omni';
import { OmniDashboard } from './pages/Dashboard';
import { OmniToolPage } from './pages/ToolPage';
import { useOmniMotion } from './hooks/useOmniMotion';
import './styles/omni-motion.css';

// ==========================================
// ROUTE REGISTRY — Semua halaman OMNI
// ==========================================
const OMNI_ROUTES: OmniRoute[] = [
    {
        path: '/',
        component: OmniDashboard,
        label: 'Dashboard',
        emoji: '⚡',
    },
    {
        path: '/tool/:id',
        component: OmniToolPage,
        label: 'Tool Execution',
        emoji: '🔧',
    },
];

// ==========================================
// APP ROOT
// ==========================================
export function App() {
    useOmniMotion(); // ⚡ Activate Cinematic DOM Engine (Mouse tracking)

    // Log SSR status saat development
    useEffect(() => {
        if (hasOmniSSR()) {
            console.log('🌐 [OMNI-SSR] Halaman ini di-render oleh Golang SSR Engine!');
            console.log('📦 Hydration state tersedia — Zero blank screen!');
        } else {
            console.log('⚛️ [OMNI-SPA] Mode Client-Side Rendering (navigasi internal)');
        }
    }, []);

    return (
        <OmniRouter>
            <div className="omni-app">
                <OmniRoutes routes={OMNI_ROUTES} />
            </div>
        </OmniRouter>
    );
}
