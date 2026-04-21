/// <reference lib="dom" />
/// <reference types="node" />
// ===========================================================================
// OMNI PIZZICATO ENGINE (TRUE KNOWLEDGE EXTRACTION)
// ===========================================================================
// Absorbed Paradigm : alemangui/pizzicato
// Logic Inherited   : TypeScript / Web Audio Source-to-Effect Connectivity Routing
// Domain Layer      : UI / Web Audio
// ===========================================================================

export interface GraphNode {
    id: string;
    type: 'source' | 'effect' | 'destination';
    connectedTo: string | null;
}

export class OmniPizzicatoEngine {
    private processingGraph: Map<string, GraphNode> = new Map();
    private connectionsMade: number = 0;

    /**
     * By studying Pizzicato, Mother learned that abstracting Web Audio essentially means
     * managing an internal 'Linked List' or 'Graph' of node IDs, mapping source buffers 
     * mathematically to Effect contexts, and ultimately to the Destination (Speakers).
     */
    constructor() {
        // System always ends at a destination.
        this.addNode({ id: "MASTER_OUT", type: "destination", connectedTo: null });
    }

    public addNode(node: GraphNode): void {
        this.processingGraph.set(node.id, node);
    }

    public connect(sourceId: string, targetId: string): boolean {
        const source = this.processingGraph.get(sourceId);
        const target = this.processingGraph.get(targetId);

        if (source && target) {
            source.connectedTo = target.id;
            this.connectionsMade++;
            return true;
        }
        return false;
    }

    public compileGraphTopology(): any[] {
        const topology = [];
        for (const node of this.processingGraph.values()) {
            topology.push({
                [node.id]: node.connectedTo ? `-> ${node.connectedTo}` : `[END]`
            });
        }
        return topology;
    }

    public diagnostics(): any {
        return {
            engine: "OmniPizzicatoEngine",
            layer: "TypeScript UI / Audio Graph",
            nodes_active: this.processingGraph.size,
            links_established: this.connectionsMade,
            learned_logic: ["node-based-audio-routing", "linked-list-graph-topology", "web-audio-api-abstraction"]
        };
    }
}

// ---------------------------------------------------------------------------
// Execution Block (Self-Contained Verification)
// ---------------------------------------------------------------------------
if (require.main === module) {
    const engine = new OmniPizzicatoEngine();
    
    // Simulate Pizzicato's syntax architecture
    engine.addNode({ id: "SineWavePlayer", type: "source", connectedTo: null });
    engine.addNode({ id: "QuadrafuzzEffect", type: "effect", connectedTo: null });
    engine.addNode({ id: "StereoPanner", type: "effect", connectedTo: null });

    // Link: Source -> Fuzz -> Panner -> Master
    engine.connect("SineWavePlayer", "QuadrafuzzEffect");
    engine.connect("QuadrafuzzEffect", "StereoPanner");
    engine.connect("StereoPanner", "MASTER_OUT");

    console.log(JSON.stringify(engine.compileGraphTopology(), null, 2));
    console.log(JSON.stringify(engine.diagnostics(), null, 2));
}
