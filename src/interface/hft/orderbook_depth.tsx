import React, { useState, useEffect } from 'react';

export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

interface PriceLevel {
    price: number;
    qty: number;
}

export const OrderBookDepth: React.FC<{ symbol: string }> = ({ symbol }) => {
    const [bids, setBids] = useState<PriceLevel[]>([]);
    const [asks, setAsks] = useState<PriceLevel[]>([]);
    const [lastPrice, setLastPrice] = useState<number>(0);

    // Simulate high-frequency updates
    useEffect(() => {
        let basePrice = 150.00;
        
        const generateBook = () => {
            const newBids = Array.from({length: 10}, (_, i) => ({
                price: basePrice - (i + 1) * 0.05,
                qty: Math.floor(Math.random() * 1000) + 100
            }));
            const newAsks = Array.from({length: 10}, (_, i) => ({
                price: basePrice + (i + 1) * 0.05,
                qty: Math.floor(Math.random() * 1000) + 100
            }));
            
            setBids(newBids);
            setAsks(newAsks);
            setLastPrice(basePrice + (Math.random() * 0.04 - 0.02));
            basePrice += (Math.random() * 0.1 - 0.05);
        };

        generateBook();
        // Extremely fast interval for HFT simulation (50ms)
        const interval = setInterval(generateBook, 50);

        return () => clearInterval(interval);
    }, [symbol]);

    const maxQty = Math.max(
        ...bids.map(b => b.qty), 
        ...asks.map(a => a.qty)
    ) || 1;

    return (
        <div style={{ backgroundColor: '#000', color: '#fff', padding: '16px', fontFamily: 'monospace', width: '300px' }}>
            <div style={{ borderBottom: '1px solid #333', paddingBottom: '8px', marginBottom: '8px', fontWeight: 'bold' }}>
                {symbol} Order Book
            </div>

            {/* Asks (Sell Orders) - Displayed in reverse order (highest at top) */}
            <div style={{ display: 'flex', flexDirection: 'column-reverse' }}>
                {asks.map((ask, i) => (
                    <DepthRow key={`ask-${i}`} level={ask} type="ask" maxQty={maxQty} />
                ))}
            </div>

            {/* Spread / Last Price */}
            <div style={{ 
                textAlign: 'center', 
                padding: '8px 0', 
                margin: '4px 0', 
                backgroundColor: '#111',
                fontSize: '1.1em',
                fontWeight: 'bold',
                color: lastPrice > (bids[0]?.price || 0) ? '#10b981' : '#ef4444'
            }}>
                {lastPrice.toFixed(2)}
            </div>

            {/* Bids (Buy Orders) */}
            <div>
                {bids.map((bid, i) => (
                    <DepthRow key={`bid-${i}`} level={bid} type="bid" maxQty={maxQty} />
                ))}
            </div>
        </div>
    );
};

const DepthRow: React.FC<{ level: PriceLevel, type: 'bid' | 'ask', maxQty: number }> = ({ level, type, maxQty }) => {
    const depthPct = (level.qty / maxQty) * 100;
    const isBid = type === 'bid';
    
    return (
        <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            position: 'relative',
            padding: '2px 4px',
            fontSize: '13px'
        }}>
            {/* Depth Visualizer Background */}
            <div style={{
                position: 'absolute',
                top: 0,
                [isBid ? 'right' : 'left']: 0,
                height: '100%',
                width: `${depthPct}%`,
                backgroundColor: isBid ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                zIndex: 0
            }} />
            
            <span style={{ color: isBid ? '#10b981' : '#ef4444', zIndex: 1 }}>{level.price.toFixed(2)}</span>
            <span style={{ color: '#9ca3af', zIndex: 1 }}>{level.qty}</span>
        </div>
    );
};
