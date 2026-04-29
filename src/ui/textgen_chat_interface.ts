// OMNI UI Layer - TextGen Chat Interface
import { JSX } from "@omni-bridge/ui/jsx";

export function ChatInterface(props: { characterName: string }): JSX.Element {
    return (
        <div className="flex flex-col h-screen bg-gray-900 text-gray-100 font-sans">
            <header className="p-4 bg-gray-800 border-b border-gray-700 shadow-md">
                <h1 className="text-lg font-bold">Chatting with {props.characterName}</h1>
            </header>
            <main className="flex-1 p-6 overflow-y-auto">
                <div className="text-center text-gray-500 italic">Conversation started.</div>
            </main>
            <footer className="p-4 bg-gray-800 border-t border-gray-700">
                <input 
                    type="text" 
                    placeholder="Type your message..." 
                    className="w-full bg-gray-700 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </footer>
        </div>
    );
}
