// OMNI UI Layer - ChatTTS Player
import { JSX } from "@omni-bridge/ui/jsx";

export function ChatTTSPlayer(props: { srcUrl: string, isPlaying: boolean }): JSX.Element {
    return (
        <div className="audio-player bg-slate-800 p-6 rounded-xl flex items-center justify-between text-white shadow-2xl">
            <div className="flex items-center space-x-4">
                <button className="bg-emerald-500 hover:bg-emerald-600 p-3 rounded-full transition">
                    {props.isPlaying ? "Pause" : "Play"}
                </button>
                <div className="text-sm font-medium">ChatTTS Voice Synthesis</div>
            </div>
            <div className="w-1/2 bg-slate-700 h-2 rounded-full overflow-hidden">
                <div className={`h-full bg-emerald-400 ${props.isPlaying ? 'w-1/2' : 'w-0'} transition-all duration-1000`}></div>
            </div>
        </div>
    );
}
