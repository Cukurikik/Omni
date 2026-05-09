// moe_node_registry.ts — Network / Orchestration
// Layer: Network / Gateways — Expert Node Registry
//
// Inspired by nr-site-registry.
// A centralized service registry built in TypeScript/Express to track the health,
// IP, and hosted experts of physical GPU nodes across the cluster.

import express from 'express';

interface ExpertNode {
    nodeId: string;
    ipAddress: string;
    vramFreeMB: number;
    hostedExperts: number[];
    lastPing: number;
}

class MoERegistry {
    private nodes: Map<string, ExpertNode> = new Map();

    public registerNode(node: ExpertNode): void {
        node.lastPing = Date.now();
        this.nodes.set(node.nodeId, node);
        console.log(`[Registry] Registered Node ${node.nodeId} hosting experts: ${node.hostedExperts}`);
    }

    public heartbeat(nodeId: string, vramFreeMB: number): void {
        const node = this.nodes.get(nodeId);
        if (node) {
            node.lastPing = Date.now();
            node.vramFreeMB = vramFreeMB;
        } else {
            console.warn(`[Registry] Received heartbeat for unknown node: ${nodeId}`);
        }
    }

    public getRoutingMap(): Record<number, string[]> {
        const routeMap: Record<number, string[]> = {};
        const now = Date.now();

        this.nodes.forEach(node => {
            // Filter out dead nodes (no ping in 30s)
            if (now - node.lastPing > 30000) return;

            node.hostedExperts.forEach(expertId => {
                if (!routeMap[expertId]) {
                    routeMap[expertId] = [];
                }
                routeMap[expertId].push(node.ipAddress);
            });
        });

        return routeMap;
    }
}

// Zero-mock initialization for universal binary structure
export function initializeRegistryAPI(): express.Express {
    const app = express();
    app.use(express.json());
    
    const registry = new MoERegistry();

    app.post('/api/nodes/register', (req, res) => {
        registry.registerNode(req.body as ExpertNode);
        res.status(200).json({ status: 'registered' });
    });

    app.post('/api/nodes/:id/heartbeat', (req, res) => {
        registry.heartbeat(req.params.id, req.body.vramFreeMB);
        res.status(200).json({ status: 'alive' });
    });

    app.get('/api/routing/map', (req, res) => {
        res.status(200).json(registry.getRoutingMap());
    });

    return app;
}
