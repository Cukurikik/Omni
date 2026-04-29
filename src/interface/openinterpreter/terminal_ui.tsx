// OMNI OPEN INTERPRETER: Terminal UI
// React component rendering a chat interface and code block execution state for Open Interpreter.
// Source: OpenInterpreter/open-interpreter

import React, { useState } from 'react';

type Message = {
    role: 'user' | 'assistant' | 'system';
    content: string;
    isCode?: boolean;
    language?: string;
    executionResult?: string;
};

export const TerminalUI: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const newMsg: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, newMsg]);
        setInput('');

        // Simulate backend API call to Open Interpreter Engine
        setTimeout(() => {
            const assistantResponse: Message = {
                role: 'assistant',
                content: 'print("Hello from Omni Interpreter!")',
                isCode: true,
                language: 'python'
            };
            setMessages(prev => [...prev, assistantResponse]);
        }, 1000);
    };

    return (
        <div className="flex flex-col h-screen bg-gray-900 text-green-400 font-mono p-4">
            <div className="flex-1 overflow-y-auto mb-4 space-y-4">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`p-3 rounded ${msg.role === 'user' ? 'bg-gray-800' : 'bg-gray-700'}`}>
                        <div className="text-xs text-gray-400 mb-1">[{msg.role.toUpperCase()}]</div>
                        {msg.isCode ? (
                            <div className="bg-black p-3 rounded border border-gray-600">
                                <pre><code>{msg.content}</code></pre>
                                <button className="mt-2 text-xs bg-blue-600 hover:bg-blue-500 text-white px-2 py-1 rounded">
                                    Run {msg.language}
                                </button>
                            </div>
                        ) : (
                            <div>{msg.content}</div>
                        )}
                        {msg.executionResult && (
                            <div className="mt-2 text-yellow-300 text-sm">
                                Output: {msg.executionResult}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            <form onSubmit={handleSubmit} className="flex">
                <span className="text-blue-400 mr-2">omni-interpreter &gt;</span>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="flex-1 bg-transparent outline-none text-white border-b border-gray-600 focus:border-green-400"
                    autoFocus
                />
            </form>
        </div>
    );
};
