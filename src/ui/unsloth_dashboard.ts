// OMNI UI Layer - Unsloth Dashboard
import { JSX } from "@omni-bridge/ui/jsx";

export function UnslothDashboard(props: { isTraining: boolean, vramUsed: number }): JSX.Element {
    return (
        <div className="unsloth-dash p-6 bg-gray-900 text-white rounded-lg shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-emerald-400">Unsloth Accelerator</h2>
            <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-800 rounded">
                    <div className="text-sm text-gray-400">Status</div>
                    <div className={`font-bold ${props.isTraining ? 'text-green-500' : 'text-yellow-500'}`}>
                        {props.isTraining ? 'Training Active (2x Speed)' : 'Idle'}
                    </div>
                </div>
                <div className="p-4 bg-gray-800 rounded">
                    <div className="text-sm text-gray-400">VRAM Usage</div>
                    <div className="font-mono">{props.vramUsed} GB</div>
                </div>
            </div>
        </div>
    );
}
