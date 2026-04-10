// ==========================================
// 🧭 OMNI-NAVIGATOR: Custom SPA Router
// ==========================================
// Framework OMNI tidak bergantung pada react-router.
// Ini adalah sistem routing mandiri berbasis hash (#).
// Semua navigasi menggunakan OmniLink dan OmniNavigate.

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

// ==========================================
// TYPES
// ==========================================
export interface OmniRoute {
    path: string;
    component: React.ComponentType<any>;
    label?: string;
    emoji?: string;
}

interface OmniRouterContextType {
    currentPath: string;
    navigate: (path: string) => void;
    params: Record<string, string>;
}

// ==========================================
// CONTEXT
// ==========================================
const OmniRouterContext = createContext<OmniRouterContextType>({
    currentPath: '/',
    navigate: () => {},
    params: {},
});

// ==========================================
// HOOKS
// ==========================================
export function useOmniRouter() {
    return useContext(OmniRouterContext);
}

export function useOmniParams() {
    return useContext(OmniRouterContext).params;
}

export function useOmniNavigate() {
    const { navigate } = useContext(OmniRouterContext);
    return navigate;
}

// ==========================================
// PATH MATCHING ENGINE
// ==========================================
function matchPath(routePath: string, currentPath: string): { match: boolean; params: Record<string, string> } {
    const routeParts = routePath.split('/').filter(Boolean);
    const currentParts = currentPath.split('/').filter(Boolean);
    const params: Record<string, string> = {};

    if (routeParts.length !== currentParts.length) {
        return { match: false, params: {} };
    }

    for (let i = 0; i < routeParts.length; i++) {
        if (routeParts[i].startsWith(':')) {
            params[routeParts[i].slice(1)] = currentParts[i];
        } else if (routeParts[i] !== currentParts[i]) {
            return { match: false, params: {} };
        }
    }

    return { match: true, params };
}

function getHashPath(): string {
    const hash = window.location.hash.slice(1);
    return hash || '/';
}

import { transitionDOM } from '../hooks/useOmniMotion';

// ==========================================
// OMNI ROUTER PROVIDER
// ==========================================
export function OmniRouter({ children }: { children: React.ReactNode }) {
    const [currentPath, setCurrentPath] = useState(getHashPath);

    useEffect(() => {
        const handleHashChange = () => {
            transitionDOM(() => setCurrentPath(getHashPath()));
        };
        window.addEventListener('hashchange', handleHashChange);
        return () => window.removeEventListener('hashchange', handleHashChange);
    }, []);

    const navigate = useCallback((path: string) => {
        window.location.hash = path;
    }, []);

    return (
        <OmniRouterContext.Provider value={{ currentPath, navigate, params: {} }}>
            {children}
        </OmniRouterContext.Provider>
    );
}

// ==========================================
// OMNI ROUTE RENDERER
// ==========================================
export function OmniRoutes({ routes }: { routes: OmniRoute[] }) {
    const { currentPath, navigate } = useOmniRouter();

    for (const route of routes) {
        const { match, params } = matchPath(route.path, currentPath);
        if (match) {
            const Component = route.component;
            return (
                <OmniRouterContext.Provider value={{ currentPath, navigate, params }}>
                    <Component />
                </OmniRouterContext.Provider>
            );
        }
    }

    // Fallback: halaman pertama (dashboard)
    const Fallback = routes[0]?.component;
    return Fallback ? <Fallback /> : null;
}

// ==========================================
// OMNI LINK COMPONENT
// ==========================================
interface OmniLinkProps {
    to: string;
    className?: string;
    activeClassName?: string;
    children: React.ReactNode;
    onClick?: () => void;
}

export function OmniLink({ to, className = '', activeClassName = 'active', children, onClick }: OmniLinkProps) {
    const { currentPath, navigate } = useOmniRouter();
    const isActive = currentPath === to;

    const handleClick = (e: React.MouseEvent) => {
        e.preventDefault();
        navigate(to);
        onClick?.();
    };

    return (
        <a
            href={`#${to}`}
            className={`${className} ${isActive ? activeClassName : ''}`}
            onClick={handleClick}
        >
            {children}
        </a>
    );
}

// ==========================================
// PROGRAMMATIC NAVIGATION
// ==========================================
export function omniNavigate(path: string) {
    window.location.hash = path;
}
