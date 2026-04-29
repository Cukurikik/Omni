// OMNI UI Layer - IM Chat Client
import { JSX } from "@omni-bridge/ui/jsx";

type ChatState = {
    userId: string;
    messages: { text: string; from: string }[];
};

export function PaiPaiClient(props: { state: ChatState }): JSX.Element {
    return (
        <div className="im-client h-full flex flex-col bg-slate-900 text-white">
            <header className="p-4 bg-slate-800">PaiPai Connected: {props.state.userId}</header>
            <div className="flex-1 p-4 overflow-auto">
                {props.state.messages.map((msg, i) => (
                    <div key={i} className={`mb-2 p-2 rounded ${msg.from === props.state.userId ? 'bg-blue-600 self-end' : 'bg-gray-700 self-start'}`}>
                        {msg.text}
                    </div>
                ))}
            </div>
        </div>
    );
}
