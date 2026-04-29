// OMNI UI Layer - H2O Studio GUI
import { JSX } from "@omni-bridge/ui/jsx";

export function H2OExperimentCard(props: { name: string, status: string, metric: number }): JSX.Element {
    return (
        <div className="h2o-card bg-white border-l-4 border-blue-500 shadow-sm p-4 rounded-md">
            <h4 className="font-bold text-gray-800 text-lg">{props.name}</h4>
            <div className="mt-2 flex justify-between items-center text-sm">
                <span className={`px-2 py-1 rounded text-white ${props.status === 'running' ? 'bg-blue-500' : 'bg-green-500'}`}>
                    {props.status.toUpperCase()}
                </span>
                <span className="font-mono text-gray-600">Val Loss: {props.metric.toFixed(3)}</span>
            </div>
        </div>
    );
}
