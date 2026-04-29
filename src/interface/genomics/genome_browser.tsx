import React, { useState, useEffect, useRef } from 'react';

export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

interface GenomeFeature {
    id: string;
    start: number;
    end: number;
    type: 'gene' | 'exon' | 'variant' | 'promoter';
    name: string;
}

export const GenomeBrowser: React.FC<{ chromosome: string }> = ({ chromosome }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [viewStart, setViewStart] = useState<number>(1000000);
    const [viewEnd, setViewEnd] = useState<number>(1005000);
    const [features, setFeatures] = useState<GenomeFeature[]>([]);

    useEffect(() => {
        // Generate mock features for the structural interface
        const mockFeatures: GenomeFeature[] = [];
        let currentPos = 1000100;
        
        for (let i = 0; i < 20; i++) {
            const length = Math.floor(Math.random() * 500) + 100;
            const typeRand = Math.random();
            const type = typeRand > 0.8 ? 'gene' : typeRand > 0.4 ? 'exon' : typeRand > 0.2 ? 'promoter' : 'variant';
            
            mockFeatures.push({
                id: `ft-${i}`,
                start: currentPos,
                end: currentPos + length,
                type: type,
                name: `${type.toUpperCase()}_${i}`
            });
            
            currentPos += length + Math.floor(Math.random() * 200);
        }
        
        setFeatures(mockFeatures);
    }, [chromosome]);

    useEffect(() => {
        drawBrowser();
    }, [viewStart, viewEnd, features]);

    const drawBrowser = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Background
        ctx.fillStyle = '#fafafa';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const viewLength = viewEnd - viewStart;
        
        // Draw axis
        ctx.beginPath();
        ctx.moveTo(0, 50);
        ctx.lineTo(canvas.width, 50);
        ctx.strokeStyle = '#cbd5e1';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Ticks
        ctx.fillStyle = '#64748b';
        ctx.font = '10px sans-serif';
        for (let i = 0; i <= 5; i++) {
            const x = (canvas.width / 5) * i;
            const pos = Math.floor(viewStart + (viewLength / 5) * i);
            
            ctx.beginPath();
            ctx.moveTo(x, 45);
            ctx.lineTo(x, 55);
            ctx.stroke();
            
            ctx.fillText(pos.toLocaleString(), x + 5, 40);
        }

        // Draw features
        features.forEach(feat => {
            if (feat.end < viewStart || feat.start > viewEnd) return; // Outside view

            const xStart = ((feat.start - viewStart) / viewLength) * canvas.width;
            const xEnd = ((feat.end - viewStart) / viewLength) * canvas.width;
            const width = Math.max(xEnd - xStart, 2); // Min 2px width
            
            let y = 80;
            let height = 15;
            let color = '#94a3b8';

            switch (feat.type) {
                case 'gene':
                    color = '#3b82f6';
                    y = 70;
                    break;
                case 'exon':
                    color = '#10b981';
                    y = 90;
                    break;
                case 'promoter':
                    color = '#eab308';
                    y = 110;
                    break;
                case 'variant':
                    color = '#ef4444';
                    y = 130;
                    height = 20;
                    break;
            }

            ctx.fillStyle = color;
            ctx.fillRect(xStart, y, width, height);
            
            if (width > 30) {
                ctx.fillStyle = '#fff';
                ctx.font = '10px sans-serif';
                ctx.fillText(feat.name, xStart + 5, y + 11);
            }
        });
    };

    const handleZoom = (direction: 'in' | 'out') => {
        const center = viewStart + (viewEnd - viewStart) / 2;
        const currentLength = viewEnd - viewStart;
        const newLength = direction === 'in' ? currentLength * 0.5 : currentLength * 2.0;
        
        setViewStart(Math.floor(center - newLength / 2));
        setViewEnd(Math.floor(center + newLength / 2));
    };

    const handlePan = (direction: 'left' | 'right') => {
        const shift = (viewEnd - viewStart) * 0.25;
        if (direction === 'left') {
            setViewStart(viewStart - shift);
            setViewEnd(viewEnd - shift);
        } else {
            setViewStart(viewStart + shift);
            setViewEnd(viewEnd + shift);
        }
    };

    return (
        <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden', fontFamily: 'system-ui, sans-serif', width: '800px' }}>
            <div style={{ backgroundColor: '#f8fafc', padding: '12px 16px', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0, color: '#334155' }}>IGV Light Browser: {chromosome}</h3>
                
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button onClick={() => handlePan('left')} style={btnStyle}>&larr;</button>
                    <button onClick={() => handleZoom('in')} style={btnStyle}>Zoom In</button>
                    <button onClick={() => handleZoom('out')} style={btnStyle}>Zoom Out</button>
                    <button onClick={() => handlePan('right')} style={btnStyle}>&rarr;</button>
                </div>
            </div>
            
            <div style={{ padding: '20px', backgroundColor: '#fff' }}>
                <canvas 
                    ref={canvasRef} 
                    width={760} 
                    height={200}
                    style={{ border: '1px solid #f1f5f9' }}
                />
            </div>
            
            <div style={{ backgroundColor: '#f8fafc', padding: '8px 16px', borderTop: '1px solid #e2e8f0', fontSize: '12px', color: '#64748b', display: 'flex', gap: '16px' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><div style={{width: 10, height: 10, backgroundColor: '#3b82f6'}}></div> Gene</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><div style={{width: 10, height: 10, backgroundColor: '#10b981'}}></div> Exon</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><div style={{width: 10, height: 10, backgroundColor: '#eab308'}}></div> Promoter</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><div style={{width: 10, height: 10, backgroundColor: '#ef4444'}}></div> Variant</span>
            </div>
        </div>
    );
};

const btnStyle = {
    padding: '4px 8px',
    backgroundColor: '#fff',
    border: '1px solid #cbd5e1',
    borderRadius: '4px',
    cursor: 'pointer',
    color: '#475569',
    fontSize: '12px'
};
