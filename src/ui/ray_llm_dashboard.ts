// OMNI UI Layer - Ray LLM Dashboard
import { JSX } from "@omni-bridge/ui/jsx";

export function RayNodeStatus(props: { nodeIp: string, gpuUtil: number, memoryUtil: number }): JSX.Element {
    return (
        <div className="border border-blue-200 p-4 rounded-md shadow-sm bg-blue-50">
            <h4 className="font-bold text-blue-900 border-b pb-1 mb-2">Ray Node: {props.nodeIp}</h4>
            <div className="flex flex-col gap-1 text-sm">
                <div>GPU Util: <span className="font-mono text-blue-700">{props.gpuUtil}%</span></div>
                <div>RAM Util: <span className="font-mono text-blue-700">{props.memoryUtil}%</span></div>
            </div>
        </div>
    );
}
