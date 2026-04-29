// OMNI UI Layer - LlamaIndex Graph Viewer
import { JSX } from "@omni-bridge/ui/jsx";

export function GraphViewer(props: { nodes: number, edges: number }): JSX.Element {
    return (
        <div className="bg-white border p-6 rounded-xl shadow-lg">
            <h2 className="text-xl font-bold text-gray-800 mb-4">LlamaIndex Knowledge Graph</h2>
            <div className="flex justify-between items-center text-sm font-medium">
                <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full">{props.nodes} Nodes</span>
                <span className="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full">{props.edges} Edges</span>
            </div>
            <div className="mt-4 h-32 border-2 border-dashed border-gray-200 flex items-center justify-center text-gray-400">
                [Graph Visualization Canvas]
            </div>
        </div>
    );
}
