import React, { useState, useEffect, useRef } from 'react';

export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

interface Asset {
    id: string;
    lat: number;
    lon: number;
    status: 'ACTIVE' | 'MAINTENANCE' | 'OFFLINE';
}

export const GISMapDashboard: React.FC = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [assets, setAssets] = useState<Asset[]>([]);
    
    // Simulate center of NYC
    const [center] = useState({ lat: 40.7128, lon: -74.0060 });
    const [zoom] = useState(12);

    useEffect(() => {
        // Generate random assets around the center
        const mockAssets: Asset[] = Array.from({ length: 150 }, (_, i) => {
            const r = 0.05 * Math.sqrt(Math.random());
            const theta = Math.random() * 2 * Math.PI;
            
            const randStatus = Math.random();
            const status = randStatus > 0.9 ? 'OFFLINE' : randStatus > 0.8 ? 'MAINTENANCE' : 'ACTIVE';

            return {
                id: `AST-${i}`,
                lat: center.lat + r * Math.cos(theta),
                lon: center.lon + r * Math.sin(theta),
                status
            };
        });

        setAssets(mockAssets);

        // Real-time movement simulation
        const interval = setInterval(() => {
            setAssets(prev => prev.map(asset => {
                if (asset.status !== 'ACTIVE') return asset;
                return {
                    ...asset,
                    lat: asset.lat + (Math.random() - 0.5) * 0.001,
                    lon: asset.lon + (Math.random() - 0.5) * 0.001
                };
            }));
        }, 2000);

        return () => clearInterval(interval);
    }, [center.lat, center.lon]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear canvas
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw dummy map grid to simulate tiles
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 1;
        for (let x = 0; x <= canvas.width; x += 100) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
        }
        for (let y = 0; y <= canvas.height; y += 100) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
        }

        // Projection math (Mercator-ish simplification for local view)
        const project = (lat: number, lon: number) => {
            const scale = Math.pow(2, zoom) * 256;
            // Extremely simplified projection focused around center
            const x = canvas.width / 2 + (lon - center.lon) * scale * 0.01;
            const y = canvas.height / 2 - (lat - center.lat) * scale * 0.01;
            return { x, y };
        };

        // Draw assets
        assets.forEach(asset => {
            const { x, y } = project(asset.lat, asset.lon);
            
            // Draw ping
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, 2 * Math.PI);
            
            if (asset.status === 'ACTIVE') {
                ctx.fillStyle = '#10b981'; // Emerald
                ctx.shadowColor = '#10b981';
            } else if (asset.status === 'MAINTENANCE') {
                ctx.fillStyle = '#f59e0b'; // Amber
                ctx.shadowColor = '#f59e0b';
            } else {
                ctx.fillStyle = '#ef4444'; // Red
                ctx.shadowColor = '#ef4444';
            }
            
            ctx.shadowBlur = 10;
            ctx.fill();
            ctx.shadowBlur = 0; // reset
        });

    }, [assets, center.lat, center.lon, zoom]);

    return (
        <div style={{ padding: '24px', backgroundColor: '#020617', color: '#f8fafc', minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <h1 style={{ margin: 0, color: '#38bdf8' }}>OMNI GIS Operations Center</h1>
                <div style={{ display: 'flex', gap: '16px' }}>
                    <StatBadge label="ACTIVE" value={assets.filter(a => a.status === 'ACTIVE').length} color="#10b981" />
                    <StatBadge label="MAINTAIN" value={assets.filter(a => a.status === 'MAINTENANCE').length} color="#f59e0b" />
                    <StatBadge label="OFFLINE" value={assets.filter(a => a.status === 'OFFLINE').length} color="#ef4444" />
                </div>
            </div>

            <div style={{ border: '2px solid #1e293b', borderRadius: '12px', overflow: 'hidden', position: 'relative' }}>
                {/* Floating UI panel */}
                <div style={{ position: 'absolute', top: '16px', left: '16px', backgroundColor: 'rgba(15, 23, 42, 0.9)', padding: '16px', borderRadius: '8px', border: '1px solid #334155', backdropFilter: 'blur(4px)', zIndex: 10 }}>
                    <h3 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#94a3b8' }}>SECTOR 4 - NEW YORK</h3>
                    <div style={{ fontSize: '12px', color: '#cbd5e1', marginBottom: '4px' }}>LAT: {center.lat.toFixed(4)}</div>
                    <div style={{ fontSize: '12px', color: '#cbd5e1', marginBottom: '4px' }}>LON: {center.lon.toFixed(4)}</div>
                    <div style={{ fontSize: '12px', color: '#cbd5e1' }}>ZOOM: {zoom}</div>
                </div>

                <canvas 
                    ref={canvasRef} 
                    width={1200} 
                    height={600}
                    style={{ display: 'block', backgroundColor: '#1e293b', width: '100%' }}
                />
            </div>
        </div>
    );
};

const StatBadge: React.FC<{label: string, value: number, color: string}> = ({label, value, color}) => (
    <div style={{ backgroundColor: '#0f172a', border: `1px solid ${color}40`, padding: '8px 16px', borderRadius: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ width: '8px', height: '8px', backgroundColor: color, borderRadius: '50%', boxShadow: `0 0 8px ${color}` }}></div>
        <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 'bold' }}>{label}</span>
        <span style={{ fontSize: '16px', color: '#fff', fontWeight: 'bold' }}>{value}</span>
    </div>
);
