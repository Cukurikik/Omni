// OMNI UI Layer - Axolotl Monitor
import { JSX } from "@omni-bridge/ui/jsx";

export function AxolotlMonitor(props: { loss: number, step: number, total: number }): JSX.Element {
    const progress = (props.step / props.total) * 100;
    
    return (
        <div className="axolotl-monitor bg-[#1e1e2e] text-[#cdd6f4] p-5 rounded font-sans shadow-lg">
            <h3 className="text-lg font-bold text-[#89b4fa] mb-3">Axolotl Training Progress</h3>
            <div className="flex justify-between mb-2">
                <span>Step: {props.step} / {props.total}</span>
                <span className="text-[#f38ba8] font-bold">Loss: {props.loss.toFixed(4)}</span>
            </div>
            <div className="w-full bg-[#313244] rounded-full h-3">
                <div className="bg-[#a6e3a1] h-3 rounded-full transition-all" style={{ width: `${progress}%` }}></div>
            </div>
        </div>
    );
}
