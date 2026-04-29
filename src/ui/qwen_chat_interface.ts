// OMNI UI Layer - Qwen Chat Interface
import { JSX } from "@omni-bridge/ui/jsx";

type Message = { role: 'user' | 'agent' | 'tool'; content: string };

export function QwenChat(props: { history: Message[] }): JSX.Element {
    return (
        <div className="qwen-chat max-w-2xl mx-auto border rounded-lg overflow-hidden shadow-xl">
            <div className="bg-blue-800 text-white p-4 font-bold">Qwen-Agent Assistant</div>
            <div className="p-4 space-y-4 h-96 overflow-y-auto bg-gray-50">
                {props.history.map((msg, i) => (
                    <div key={i} className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-100 ml-auto w-3/4' : 'bg-white border w-3/4'}`}>
                        <span className="text-xs text-gray-500 uppercase">{msg.role}</span>
                        <p className="mt-1">{msg.content}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
