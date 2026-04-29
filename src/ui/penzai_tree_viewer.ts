// OMNI UI Layer - Penzai Tree Viewer
import { JSX } from "@omni-bridge/ui/jsx";

export function PyTreeViewer(props: { nodes: {layer: string, type: string}[] }): JSX.Element {
    return (
        <div className="bg-gray-100 p-4 rounded font-mono text-sm border shadow-inner">
            <h3 className="font-bold mb-2 text-purple-700">Penzai Model Tree</h3>
            <ul>
                {props.nodes.map((node, i) => (
                    <li key={i} className="py-1 border-b border-gray-300">
                        <span className="text-blue-600">{node.layer}</span> : <span className="text-gray-500">{node.type}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}
