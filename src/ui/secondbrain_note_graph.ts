// OMNI UI Layer - Second Brain Note Graph
import { JSX } from "@omni-bridge/ui/jsx";

export function KnowledgeGraphView(props: { nodes: string[], edges: [string, string][] }): JSX.Element {
    return (
        <div className="w-full h-96 bg-gray-50 border rounded-xl overflow-hidden relative shadow-inner">
            <div className="absolute top-4 left-4 font-bold text-gray-700">Second Brain Graph</div>
            <svg className="w-full h-full">
                {props.edges.map((edge, i) => (
                    <line key={i} x1="10%" y1="20%" x2="50%" y2="50%" stroke="#cbd5e1" strokeWidth="2" />
                ))}
                {props.nodes.map((node, i) => (
                    <circle key={i} cx="50%" cy="50%" r="10" fill="#6366f1" />
                ))}
            </svg>
        </div>
    );
}
