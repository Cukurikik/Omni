// OMNI UI Layer - Triton Kernel Profiler
import { JSX } from "@omni-bridge/ui/jsx";

export function KernelProfilerPanel(props: { kernelName: string, latencyMs: number, occupancy: number }): JSX.Element {
    return (
        <div className="bg-gray-900 text-green-400 p-6 rounded shadow-lg font-mono">
            <h2 className="text-xl font-bold border-b border-green-700 pb-2 mb-4">Triton Profiler: {props.kernelName}</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <span className="text-gray-400">Execution Time:</span>
                    <br/>
                    <span className="text-2xl">{props.latencyMs.toFixed(3)} ms</span>
                </div>
                <div>
                    <span className="text-gray-400">SM Occupancy:</span>
                    <br/>
                    <span className="text-2xl">{(props.occupancy * 100).toFixed(1)}%</span>
                </div>
            </div>
        </div>
    );
}
