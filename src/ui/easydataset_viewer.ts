// OMNI UI Layer - EasyDataset Viewer
import { JSX } from "@omni-bridge/ui/jsx";

export function DatasetViewer(props: { totalItems: number, items: string[] }): JSX.Element {
    return (
        <div className="dataset-viewer bg-white text-black p-6 rounded shadow-md border">
            <h2 className="text-lg font-bold border-b pb-2 mb-4">Dataset Preview ({props.totalItems} items)</h2>
            <ul className="space-y-2 h-64 overflow-y-auto">
                {props.items.map((item, i) => (
                    <li key={i} className="p-2 bg-gray-50 border rounded text-sm font-mono text-gray-700">
                        {item}
                    </li>
                ))}
            </ul>
        </div>
    );
}
