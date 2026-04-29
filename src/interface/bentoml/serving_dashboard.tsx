import React, { useEffect, useState } from 'react';

export const ServingDashboard = () => {
    const [metrics, setMetrics] = useState({ requests: 0, latency: 0 });

    useEffect(() => {
        const interval = setInterval(() => {
            setMetrics(m => ({ requests: m.requests + Math.floor(Math.random() * 10), latency: 15 + Math.random() * 5 }));
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bentoml-dashboard">
            <h2>Serving Dashboard</h2>
            <p>Total Requests: {metrics.requests}</p>
            <p>Avg Latency: {metrics.latency.toFixed(2)} ms</p>
        </div>
    );
};
