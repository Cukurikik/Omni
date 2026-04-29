export class ArchRenderer {
    private svgElement: SVGSVGElement;

    constructor(containerId: string) {
        const container = document.getElementById(containerId);
        this.svgElement = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        this.svgElement.setAttribute("width", "100%");
        this.svgElement.setAttribute("height", "500px");
        if (container) container.appendChild(this.svgElement);
    }

    // OMNI Engine: NN-SVG LeNet style renderer
    public drawLayer(nodes: number, x: number, radius: number = 10) {
        const spacing = 30;
        const startY = 250 - ((nodes - 1) * spacing) / 2;

        for (let i = 0; i < nodes; i++) {
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", x.toString());
            circle.setAttribute("cy", (startY + i * spacing).toString());
            circle.setAttribute("r", radius.toString());
            circle.setAttribute("fill", "#3498db");
            circle.setAttribute("stroke", "#2980b9");
            this.svgElement.appendChild(circle);
        }
    }

    public drawConnections(nodesA: number, xA: number, nodesB: number, xB: number) {
        const spacingA = 30;
        const spacingB = 30;
        const startYA = 250 - ((nodesA - 1) * spacingA) / 2;
        const startYB = 250 - ((nodesB - 1) * spacingB) / 2;

        for (let i = 0; i < nodesA; i++) {
            for (let j = 0; j < nodesB; j++) {
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", xA.toString());
                line.setAttribute("y1", (startYA + i * spacingA).toString());
                line.setAttribute("x2", xB.toString());
                line.setAttribute("y2", (startYB + j * spacingB).toString());
                line.setAttribute("stroke", "rgba(0,0,0,0.1)");
                this.svgElement.appendChild(line);
            }
        }
    }
}
