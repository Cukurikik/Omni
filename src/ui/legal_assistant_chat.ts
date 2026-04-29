// OMNI UI Layer - Legal Assistant Chat
import { JSX } from "@omni-bridge/ui/jsx";

type ChatState = {
    messages: { role: string; content: string }[];
    isDrafting: boolean;
};

export function LegalAssistantChat(props: { state: ChatState }): JSX.Element {
    return (
        <div className="legal-chat p-6 bg-slate-50">
            <h2 className="text-xl font-bold text-slate-800">Indian-LawyerGPT AI</h2>
            <div className="chat-window border rounded p-4 mt-4 bg-white shadow">
                {props.state.messages.map((msg, i) => (
                    <div key={i} className={`msg ${msg.role} p-2 border-b`}>
                        <strong className="capitalize">{msg.role}:</strong> {msg.content}
                    </div>
                ))}
                {props.state.isDrafting && <div className="text-gray-400 italic">Drafting legal response...</div>}
            </div>
        </div>
    );
}
