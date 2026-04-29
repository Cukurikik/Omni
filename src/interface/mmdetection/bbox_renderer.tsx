import React, { useRef, useEffect } from 'react';

// OMNI MMDETECTION: Bounding Box Renderer
// React TSX canvas overlay to render detected objects and confidence scores.
// Source: open-mmlab/mmdetection

interface BoundingBox {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    label: string;
    confidence: number;
}

interface BBoxRendererProps {
    imageUrl: string;
    imageWidth: number;
    imageHeight: number;
    boxes: BoundingBox[];
}

export const BBoxRenderer: React.FC<BBoxRendererProps> = ({ imageUrl, imageWidth, imageHeight, boxes }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear previous drawing
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw image background (simulated via an Image object)
        const img = new Image();
        img.src = imageUrl;
        img.onload = () => {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            // Render bounding boxes
            boxes.forEach(box => {
                const width = box.x2 - box.x1;
                const height = box.y2 - box.y1;

                // Box
                ctx.strokeStyle = '#00ff00';
                ctx.lineWidth = 2;
                ctx.strokeRect(box.x1, box.y1, width, height);

                // Label Background
                ctx.fillStyle = '#00ff00';
                const text = `${box.label} ${(box.confidence * 100).toFixed(1)}%`;
                const textWidth = ctx.measureText(text).width;
                ctx.fillRect(box.x1, box.y1 - 20, textWidth + 10, 20);

                // Label Text
                ctx.fillStyle = '#000000';
                ctx.font = '12px Arial';
                ctx.fillText(text, box.x1 + 5, box.y1 - 5);
            });
        };
    }, [imageUrl, boxes, imageWidth, imageHeight]);

    return (
        <div style={{ position: 'relative', width: `${imageWidth}px`, height: `${imageHeight}px` }}>
            <canvas 
                ref={canvasRef} 
                width={imageWidth} 
                height={imageHeight}
                style={{ position: 'absolute', top: 0, left: 0, borderRadius: '8px', boxShadow: '0 4px 8px rgba(0,0,0,0.5)' }}
            />
        </div>
    );
};
