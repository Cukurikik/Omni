// OMNI TypeScript Interface Layer: MuJoCo Physics Viewer
// Three.js renderer for DeepMind dm_control MuJoCo environments.

import * as THREE from 'three';

export class MuJoCoViewer {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private entities: Map<string, THREE.Mesh> = new Map();

    constructor(canvas: HTMLCanvasElement) {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);

        this.camera = new THREE.PerspectiveCamera(75, canvas.width / canvas.height, 0.1, 1000);
        this.camera.position.set(0, 2, 5);
        this.camera.lookAt(0, 0, 0);

        this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
        
        // Lighting
        const ambient = new THREE.AmbientLight(0x404040);
        const directional = new THREE.DirectionalLight(0xffffff, 1);
        directional.position.set(5, 10, 5);
        this.scene.add(ambient, directional);

        // Ground plane
        const plane = new THREE.Mesh(
            new THREE.PlaneGeometry(20, 20),
            new THREE.MeshStandardMaterial({ color: 0x2a2a3e, depthWrite: false })
        );
        plane.rotation.x = -Math.PI / 2;
        this.scene.add(plane);
    }

    public updateState(state: { id: string, type: 'box' | 'sphere', pos: [number, number, number], rot: [number, number, number] }[]) {
        // Sync entities with physics engine state
        for (const entity of state) {
            let mesh = this.entities.get(entity.id);
            if (!mesh) {
                const geo = entity.type === 'box' 
                    ? new THREE.BoxGeometry(0.5, 0.5, 0.5) 
                    : new THREE.SphereGeometry(0.25);
                const mat = new THREE.MeshStandardMaterial({ color: 0x00ff88 });
                mesh = new THREE.Mesh(geo, mat);
                this.scene.add(mesh);
                this.entities.set(entity.id, mesh);
            }
            
            mesh.position.set(entity.pos[0], entity.pos[1], entity.pos[2]);
            mesh.rotation.set(entity.rot[0], entity.rot[1], entity.rot[2]);
        }
        
        this.renderer.render(this.scene, this.camera);
    }
}
