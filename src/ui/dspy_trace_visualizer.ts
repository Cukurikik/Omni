// OMNI UI Layer - DSPy Trace Visualizer
import { JSX } from "@omni-bridge/ui/jsx";

export function TraceVisualizer(props: { moduleName: string, latencyMs: number }): JSX.Element {
    return (
        <div className="bg-slate-900 text-slate-100 p-5 rounded-md shadow-inner border border-slate-700">
            <h3 className="text-lg font-semibold text-teal-400 font-mono flex items-center gap-2">
                <span className="bg-teal-900 px-2 py-0.5 rounded text-xs text-teal-200">DSPy Mod</span>
                {props.moduleName}
            </h3>
            <div className="mt-3 text-sm text-slate-400">
                Execution Latency: <span className="font-mono text-amber-400">{props.latencyMs} ms</span>
            </div>
        </div>
    );
}
