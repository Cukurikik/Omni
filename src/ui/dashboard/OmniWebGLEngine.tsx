import React, { useEffect, useRef } from 'react';

// OmniWebGLEngine.tsx — WebGL Rendering Context Wrapper
// Layer: Interface / TypeScript
//
// Provides a low-level WebGL 2.0 rendering context directly integrated
// into the React component lifecycle. Used for massive data visualization
// (e.g., 3D point clouds) bypassing standard DOM manipulation. Zero mock.

export interface OmniWebGLEngineProps {
    width: number;
    height: number;
    className?: string;
    // Callback where standard WebGL commands (bindBuffer, drawArrays) execute
    onRender: (gl: WebGL2RenderingContext, frameTime: number) => void;
    // Callback to initialize shaders and buffers once
    onInit?: (gl: WebGL2RenderingContext) => void;
}

export const OmniWebGLEngine: React.FC<OmniWebGLEngineProps> = ({
    width,
    height,
    className = '',
    onRender,
    onInit
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const requestRef = useRef<number>();
    const prevTimeRef = useRef<number>();
    const isInitialized = useRef<boolean>(false);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const gl = canvas.getContext('webgl2', {
            alpha: false,
            antialias: true,
            depth: true,
            powerPreference: "high-performance"
        });

        if (!gl) {
            console.error("WebGL 2.0 not supported by this browser/device.");
            return;
        }

        if (!isInitialized.current && onInit) {
            onInit(gl);
            isInitialized.current = true;
        }

        const renderLoop = (time: number) => {
            if (prevTimeRef.current !== undefined) {
                const deltaTime = time - prevTimeRef.current;
                
                // Clear the canvas
                gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);
                gl.clearColor(0.0, 0.0, 0.0, 1.0); // Black background
                gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

                // Execute custom render logic
                onRender(gl, deltaTime);
            }
            prevTimeRef.current = time;
            requestRef.current = requestAnimationFrame(renderLoop);
        };

        requestRef.current = requestAnimationFrame(renderLoop);

        return () => {
            if (requestRef.current) {
                cancelAnimationFrame(requestRef.current);
            }
        };
    }, [onRender, onInit]);

    return (
        <canvas
            ref={canvasRef}
            width={width}
            height={height}
            className={`block rounded-lg shadow-2xl ${className}`}
            style={{ width: `${width}px`, height: `${height}px` }}
            aria-label="Interactive 3D WebGL Visualization"
            role="img"
        />
    );
};
