// ==========================================
// ⚛️ OMNI-SSR: React Hydration Hook
// ==========================================
// Membaca data yang disuntikkan oleh Golang SSR Engine
// ke dalam window.__OMNI_INITIAL_STATE__
//
// Jika data ada → React langsung render tanpa loading spinner
// Jika data null → React fetch API seperti biasa (SPA mode)
// ==========================================

import { useState, useEffect, useCallback } from 'react';

// Type declaration untuk window global
declare global {
    interface Window {
        __OMNI_INITIAL_STATE__?: Record<string, unknown>;
    }
}

interface UseOmniSSRResult<T> {
    /** Data dari SSR atau fetch result */
    data: T | null;
    /** True jika data berasal dari SSR injection */
    isSSR: boolean;
    /** True jika sedang fetching (hanya di SPA mode) */
    isLoading: boolean;
    /** Error message jika fetch gagal */
    error: string | null;
}

/**
 * useOmniSSR — Custom Hook untuk OMNI SSR Hydration
 * 
 * @param key - Key di dalam __OMNI_INITIAL_STATE__ object
 * @param fetchUrl - URL API untuk fallback fetch (SPA mode)
 * @returns { data, isSSR, isLoading, error }
 * 
 * @example
 * ```tsx
 * const { data, isSSR, isLoading } = useOmniSSR('dashboard', '/api/v1/dashboard');
 * if (isLoading) return <Spinner />;
 * return <Dashboard data={data} />;
 * ```
 */
export function useOmniSSR<T = unknown>(key?: string, fetchUrl?: string): UseOmniSSRResult<T> {
    // Cek apakah ada data SSR dari Golang
    const ssrState = typeof window !== 'undefined' ? window.__OMNI_INITIAL_STATE__ : null;
    const ssrData = ssrState ? (key ? ssrState[key] as T : ssrState as unknown as T) : null;

    const [data, setData] = useState<T | null>(ssrData);
    const [isSSR] = useState<boolean>(!!ssrData);
    const [isLoading, setIsLoading] = useState<boolean>(!ssrData && !!fetchUrl);
    const [error, setError] = useState<string | null>(null);

    // Bersihkan SSR state setelah hydration pertama (memory cleanup)
    useEffect(() => {
        if (ssrData && typeof window !== 'undefined') {
            // Hapus setelah React selesai hydrate agar tidak bocor memori
            const timer = setTimeout(() => {
                delete window.__OMNI_INITIAL_STATE__;
            }, 100);
            return () => clearTimeout(timer);
        }
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    // Fallback: Fetch API jika tidak ada data SSR (mode SPA/navigasi client)
    useEffect(() => {
        if (!ssrData && fetchUrl) {
            setIsLoading(true);
            fetch(fetchUrl)
                .then(res => {
                    if (!res.ok) throw new Error(`HTTP ${res.status}`);
                    return res.json();
                })
                .then(result => {
                    setData(result.data || result);
                    setIsLoading(false);
                })
                .catch(err => {
                    setError(err.message);
                    setIsLoading(false);
                });
        }
    }, [fetchUrl]); // eslint-disable-line react-hooks/exhaustive-deps

    return { data, isSSR, isLoading, error };
}

/**
 * getOmniSSRState — Ambil seluruh SSR state tanpa hook (untuk non-component code)
 */
export function getOmniSSRState(): Record<string, unknown> | null {
    if (typeof window !== 'undefined' && window.__OMNI_INITIAL_STATE__) {
        return window.__OMNI_INITIAL_STATE__;
    }
    return null;
}

/**
 * hasOmniSSR — Cek apakah halaman ini di-render oleh SSR
 */
export function hasOmniSSR(): boolean {
    return typeof window !== 'undefined' && !!window.__OMNI_INITIAL_STATE__;
}
