// OMNI UI Layer - AIGC Explorer
import { JSX } from "@omni-bridge/ui/jsx";

type Group = { name: string; focus: string };

export function AIGCExplorer(props: { groups: Group[] }): JSX.Element {
    return (
        <div className="explorer grid grid-cols-3 gap-4 p-8 bg-gray-50">
            {props.groups.map(g => (
                <div key={g.name} className="card p-4 bg-white shadow rounded hover:shadow-lg transition">
                    <h3 className="font-bold text-lg text-indigo-700">{g.name}</h3>
                    <p className="text-sm text-gray-600 mt-2">{g.focus}</p>
                </div>
            ))}
        </div>
    );
}
