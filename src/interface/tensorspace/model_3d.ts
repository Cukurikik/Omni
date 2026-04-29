/**
 * OMNI Interface Layer: TensorSpace 3D Model Renderer
 * Renders Neural Network layers in WebGL space.
 */

import { Scene, PerspectiveCamera, WebGLRenderer, BoxGeometry, MeshBasicMaterial, Mesh } from 'three';

export interface LayerConfig {
    id: string;
    type: 'Conv2D' | 'Dense' | 'Pooling';
    dimensions: [number, number, number];
    position: [number, number, number];
}

export class TensorSpaceRenderer {
    private scene: Scene;
    private camera: PerspectiveCamera;
    private renderer: WebGLRenderer;
    private layers: Map<string, Mesh>;

    constructor(canvasId: string) {
        const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!canvas) throw new Error("[OMNI] Canvas not found for TensorSpace.");

        this.scene = new Scene();
        this.camera = new PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.z = 50;

        this.renderer = new WebGLRenderer({ canvas, antialias: true, alpha: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.layers = new Map();
    }

    public addLayer(config: LayerConfig): void {
        // Visualizing dimensions x, y, z -> width, height, depth
        const geometry = new BoxGeometry(config.dimensions[0], config.dimensions[1], config.dimensions[2]);
        
        let color = 0x00ff00;
        if (config.type === 'Dense') color = 0xff0000;
        else if (config.type === 'Pooling') color = 0x0000ff;

        const material = new MeshBasicMaterial({ color, wireframe: true });
        const mesh = new Mesh(geometry, material);

        mesh.position.set(config.position[0], config.position[1], config.position[2]);
        this.scene.add(mesh);
        this.layers.set(config.id, mesh);
    }

    public animate(): void {
        requestAnimationFrame(() => this.animate());
        
        // Idle rotation for dynamics
        this.layers.forEach((mesh) => {
            mesh.rotation.y += 0.005;
            mesh.rotation.x += 0.002;
        });

        this.renderer.render(this.scene, this.camera);
    }
}
