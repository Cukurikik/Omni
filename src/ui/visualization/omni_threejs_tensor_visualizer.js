// OMNI UI & Visualization Layer
// Three.js 3D Tensor Visualizer
// Based on mrdoob/three.js. Used to visualize 3D tensor parallelism in the browser.

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

export class OmniThreejsTensorVisualizer {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private controls: OrbitControls;

    constructor(containerId: string) {
        console.log(`OMNI JS: Initializing Three.js 3D Tensor Visualizer on #${containerId}`);
        const container = document.getElementById(containerId);
        
        if (!container) throw new Error(`Container #${containerId} not found.`);

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a1a);

        this.camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        this.camera.position.z = 5;
        this.camera.position.y = 2;

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(this.renderer.domElement);

        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;

        this.addLighting();
        this.animate();
    }

    private addLighting() {
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 20, 10);
        this.scene.add(directionalLight);
    }

    public renderTensorGrid(dimensions: number[], values: Float32Array) {
        // Clear existing meshes
        this.scene.children = this.scene.children.filter(c => !(c instanceof THREE.Mesh));

        console.log(`OMNI JS: Rendering 3D Tensor grid. Dimensions: [${dimensions.join(', ')}]`);

        // Create a 3D grid of cubes representing tensor activations
        const [dimX, dimY, dimZ] = dimensions;
        const spacing = 1.2;

        const geometry = new THREE.BoxGeometry(1, 1, 1);

        for (let x = 0; x < dimX; x++) {
            for (let y = 0; y < dimY; y++) {
                for (let z = 0; z < dimZ; z++) {
                    const idx = x * dimY * dimZ + y * dimZ + z;
                    const val = values[idx];

                    // Map value to color (Red for high positive, Blue for high negative)
                    const color = new THREE.Color();
                    if (val > 0) color.setHSL(0.0, 1.0, 0.5 + (val * 0.5)); // Reddish
                    else color.setHSL(0.6, 1.0, 0.5 + (Math.abs(val) * 0.5)); // Blueish

                    const material = new THREE.MeshPhongMaterial({ 
                        color: color,
                        transparent: true,
                        opacity: Math.max(0.2, Math.abs(val)) // Low values are transparent
                    });

                    const cube = new THREE.Mesh(geometry, material);
                    
                    cube.position.set(
                        (x - dimX / 2) * spacing,
                        (y - dimY / 2) * spacing,
                        (z - dimZ / 2) * spacing
                    );

                    this.scene.add(cube);
                }
            }
        }
    }

    private animate = () => {
        requestAnimationFrame(this.animate);
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}
