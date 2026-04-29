import React, { useEffect, useRef, useState } from 'react';
// Assuming three.js is available in standard environment
import * as THREE from 'three';

interface LossPoint {
    x: number; // param 1
    y: number; // param 2
    z: number; // loss
}

interface LossSurfaceProps {
    data: LossPoint[];
    width: number;
    height: number;
}

export const OmniLossSurface3D: React.FC<LossSurfaceProps> = ({ data, width, height }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        if (data.length === 0) return;

        let scene: THREE.Scene, camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer;
        
        try {
            // Setup Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color('#0f172a'); // OMNI dark theme

            // Setup Camera
            camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
            camera.position.set(20, 20, 20);
            camera.lookAt(0, 0, 0);

            // Setup Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(width, height);
            
            // Clear previous children
            while (containerRef.current.firstChild) {
                containerRef.current.removeChild(containerRef.current.firstChild);
            }
            containerRef.current.appendChild(renderer.domElement);

            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 2);
            scene.add(ambientLight);
            
            const dirLight = new THREE.DirectionalLight(0xffffff, 1);
            dirLight.position.set(10, 20, 10);
            scene.add(dirLight);

            // Geometry Generation (Points for scatter plot)
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(data.length * 3);
            const colors = new Float32Array(data.length * 3);

            let maxZ = -Infinity;
            let minZ = Infinity;
            data.forEach(p => {
                if (p.z > maxZ) maxZ = p.z;
                if (p.z < minZ) minZ = p.z;
            });

            data.forEach((p, i) => {
                positions[i * 3] = p.x;
                positions[i * 3 + 1] = p.z; // Y is up in ThreeJS
                positions[i * 3 + 2] = p.y;

                // Color gradient based on loss
                const intensity = (p.z - minZ) / (maxZ - minZ + 1e-5);
                colors[i * 3] = intensity; // Red channel
                colors[i * 3 + 1] = 0.2; // Green
                colors[i * 3 + 2] = 1.0 - intensity; // Blue channel
            });

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            const material = new THREE.PointsMaterial({
                size: 0.5,
                vertexColors: true,
                transparent: true,
                opacity: 0.8
            });

            const pointCloud = new THREE.Points(geometry, material);
            scene.add(pointCloud);

            // Axis Helpers
            const axesHelper = new THREE.AxesHelper(10);
            scene.add(axesHelper);

            // Animation Loop
            let animationFrameId: number;
            const animate = () => {
                animationFrameId = requestAnimationFrame(animate);
                pointCloud.rotation.y += 0.005; // Auto rotate
                renderer.render(scene, camera);
            };
            animate();

            // Cleanup
            return () => {
                cancelAnimationFrame(animationFrameId);
                geometry.dispose();
                material.dispose();
                renderer.dispose();
            };

        } catch (err) {
            setError(`WebGL Initialization failed: ${err}`);
        }
    }, [data, width, height]);

    return (
        <div className="omni-loss-surface-container rounded-lg shadow-xl overflow-hidden border border-slate-700">
            {error ? (
                <div className="p-4 text-red-400 font-mono text-sm">Error: {error}</div>
            ) : (
                <div ref={containerRef} style={{ width, height }} />
            )}
        </div>
    );
};
