// OMNI UI & Visualization Layer
// D3.js Network Topology Visualization
// Based on d3/d3. Visualizes the internal state of the Omni Universal Engine.

import * as d3 from 'd3';
import { OmniIpcClient } from '@omni-bridge/system/ipc';

interface Node extends d3.SimulationNodeDatum {
    id: string;
    group: number;
    radius: number;
}

interface Link extends d3.SimulationLinkDatum<Node> {
    source: string;
    target: string;
    value: number;
}

export class OmniD3NetworkVisualizer {
    private svg: d3.Selection<SVGSVGElement, unknown, HTMLElement, any>;
    private simulation: d3.Simulation<Node, Link>;
    private width: number;
    private height: number;

    constructor(containerId: string, width: number = 800, height: number = 600) {
        console.log(`OMNI TS: Initializing D3 Network Visualizer in #${containerId}`);
        this.width = width;
        this.height = height;

        this.svg = d3.select(`#${containerId}`)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', [0, 0, width, height]);

        this.simulation = d3.forceSimulation<Node>()
            .force('link', d3.forceLink<Node, Link>().id(d => d.id).distance(50))
            .force('charge', d3.forceManyBody().strength(-100))
            .force('center', d3.forceCenter(width / 2, height / 2));
    }

    public async renderLiveClusterState() {
        // Fetch graph data from the Omni Universal Binary via IPC
        const graphData = await OmniIpcClient.request('cluster.topology', {});
        const nodes: Node[] = graphData.nodes;
        const links: Link[] = graphData.links;

        const link = this.svg.append('g')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('stroke-width', d => Math.sqrt(d.value));

        const node = this.svg.append('g')
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)
            .selectAll('circle')
            .data(nodes)
            .join('circle')
            .attr('r', d => d.radius)
            .attr('fill', d => d3.schemeCategory10[d.group % 10]);

        node.append('title')
            .text(d => d.id);

        this.simulation
            .nodes(nodes)
            .on('tick', () => {
                link
                    .attr('x1', d => (d.source as Node).x!)
                    .attr('y1', d => (d.source as Node).y!)
                    .attr('x2', d => (d.target as Node).x!)
                    .attr('y2', d => (d.target as Node).y!);

                node
                    .attr('cx', d => d.x!)
                    .attr('cy', d => d.y!);
            });

        const forceLink = this.simulation.force<d3.ForceLink<Node, Link>>('link');
        if (forceLink) {
            forceLink.links(links);
        }
    }
}
