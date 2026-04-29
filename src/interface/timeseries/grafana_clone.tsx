import React, { useState, useEffect } from 'react';

export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

interface DataPoint {
    timestamp: number;
    value: number;
}

export const TimeSeriesDashboard: React.FC = () => {
    const [data, setData] = useState<DataPoint[]>([]);
    const [cpuUsage, setCpuUsage] = useState(45);
    const [memUsage, setMemUsage] = useState(62);

    useEffect(() => {
        // Initialize history
        const now = Date.now();
        const history: DataPoint[] = [];
        let val = 100;
        
        for (let i = 60; i >= 0; i--) {
            history.push({
                timestamp: now - i * 1000,
                value: val
            });
            val += (Math.random() - 0.5) * 10;
        }
        setData(history);

        // Live updates
        const interval = setInterval(() => {
            setData(prev => {
                const lastVal = prev[prev.length - 1].value;
                const nextVal = lastVal + (Math.random() - 0.5) * 10;
                
                setCpuUsage(Math.min(100, Math.max(0, cpuUsage + (Math.random() - 0.5) * 5)));
                setMemUsage(Math.min(100, Math.max(0, memUsage + (Math.random() - 0.5) * 2)));

                return [...prev.slice(1), { timestamp: Date.now(), value: nextVal }];
            });
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    const renderPath = () => {
        if (data.length === 0) return "";
        
        const minTime = data[0].timestamp;
        const maxTime = data[data.length - 1].timestamp;
        
        const minVal = Math.min(...data.map(d => d.value)) * 0.9;
        const maxVal = Math.max(...data.map(d => d.value)) * 1.1;
        
        const width = 800;
        const height = 300;

        return data.map((d, i) => {
            const x = ((d.timestamp - minTime) / (maxTime - minTime)) * width;
            const y = height - ((d.value - minVal) / (maxVal - minVal)) * height;
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
        }).join(" ");
    };

    return (
        <div style={{ backgroundColor: '#111217', color: '#d8d9da', padding: '24px', minHeight: '100vh', fontFamily: 'Roboto, sans-serif' }}>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <h1 style={{ margin: 0, fontSize: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ color: '#F05A28', fontSize: '24px' }}>◱</span> OmniGraf Metrics
                </h1>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <select style={{ backgroundColor: '#22252b', border: '1px solid #333', color: '#fff', padding: '6px 12px', borderRadius: '2px' }}>
                        <option>Last 1 hour</option>
                        <option>Last 6 hours</option>
                        <option>Last 24 hours</option>
                    </select>
                    <button style={{ backgroundColor: '#3274d9', color: '#fff', border: 'none', padding: '6px 16px', borderRadius: '2px', cursor: 'pointer' }}>
                        Refresh
                    </button>
                </div>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '16px' }}>
                <GaugePanel title="CPU Usage" value={cpuUsage} unit="%" color="#eab308" />
                <GaugePanel title="Memory Usage" value={memUsage} unit="%" color="#3b82f6" />
                <GaugePanel title="Active Req" value={Math.floor(Math.random() * 500 + 200)} unit="req/s" color="#10b981" />
                <GaugePanel title="Error Rate" value={Math.random() * 2} unit="%" color="#ef4444" />
            </div>

            <div style={{ backgroundColor: '#22252b', border: '1px solid #333', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ padding: '8px 16px', borderBottom: '1px solid #333', fontWeight: 'bold', fontSize: '14px', cursor: 'move' }}>
                    Network Throughput (Tx/Rx)
                </div>
                <div style={{ padding: '16px', position: 'relative', height: '300px' }}>
                    {/* SVG Chart */}
                    <svg width="100%" height="100%" viewBox="0 0 800 300" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="fillGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#3274d9" stopOpacity="0.4" />
                                <stop offset="100%" stopColor="#3274d9" stopOpacity="0.0" />
                            </linearGradient>
                        </defs>
                        
                        {/* Grid lines */}
                        <line x1="0" y1="75" x2="800" y2="75" stroke="#333" strokeDasharray="4" />
                        <line x1="0" y1="150" x2="800" y2="150" stroke="#333" strokeDasharray="4" />
                        <line x1="0" y1="225" x2="800" y2="225" stroke="#333" strokeDasharray="4" />

                        <path 
                            d={`${renderPath()} L 800 300 L 0 300 Z`} 
                            fill="url(#fillGrad)" 
                        />
                        <path 
                            d={renderPath()} 
                            fill="none" 
                            stroke="#3274d9" 
                            strokeWidth="2" 
                            strokeLinejoin="round"
                        />
                    </svg>
                </div>
            </div>
        </div>
    );
};

const GaugePanel: React.FC<{title: string, value: number, unit: string, color: string}> = ({title, value, unit, color}) => (
    <div style={{ backgroundColor: '#22252b', border: '1px solid #333', borderRadius: '4px', padding: '16px', textAlign: 'center' }}>
        <div style={{ fontSize: '12px', color: '#999', marginBottom: '8px', textAlign: 'left' }}>{title}</div>
        <div style={{ fontSize: '32px', fontWeight: 'bold', color: color }}>
            {value.toFixed(1)} <span style={{ fontSize: '16px', color: '#999' }}>{unit}</span>
        </div>
    </div>
);
