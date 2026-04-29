// OMNI UI Layer - Prompt Desk Studio
import { JSX } from "@omni-bridge/ui/jsx";

type DeskState = {
    promptId: string;
    template: string;
    metrics: { latency: number; cost: number };
};

export function PromptDeskStudio(props: { state: DeskState }): JSX.Element {
    return (
        <div className="promptdesk-studio border border-slate-200 rounded p-6">
            <h2 className="text-2xl font-bold mb-4">Prompt Engineering Studio</h2>
            <div className="editor-pane bg-slate-900 text-green-400 p-4 font-mono rounded">
                {props.state.template}
            </div>
            <div className="metrics mt-4 flex gap-4">
                <div className="metric card p-2 bg-white shadow rounded">
                    Latency: {props.state.metrics.latency}ms
                </div>
                <div className="metric card p-2 bg-white shadow rounded">
                    Est. Cost: ${props.state.metrics.cost.toFixed(4)}
                </div>
            </div>
        </div>
    );
}
