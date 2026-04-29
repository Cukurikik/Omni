import React, { useState, useEffect } from 'react';

// OMNI CHATOLLAMA: Web UI
// React/Next.js frontend for interacting with local Ollama models.
// Source: ollama-webui / open-webui

type Message = {
    role: 'user' | 'assistant';
    content: string;
};

export const ChatOllamaUI: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [models, setModels] = useState<string[]>(['llama3', 'mistral', 'phi3']);
    const [selectedModel, setSelectedModel] = useState('llama3');
    const [isGenerating, setIsGenerating] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isGenerating) return;

        const userMsg: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsGenerating(true);

        // Add empty assistant message to append to
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

        try {
            // Simulated Streaming API Call
            const streamContent = ["Hello! ", "I am ", selectedModel, " running locally. ", "How can I help?"];
            for (let i = 0; i < streamContent.length; i++) {
                await new Promise(r => setTimeout(r, 200));
                setMessages(prev => {
                    const newMsgs = [...prev];
                    newMsgs[newMsgs.length - 1].content += streamContent[i];
                    return newMsgs;
                });
            }
        } catch (error) {
            console.error(error);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-900 text-gray-100 p-6">
            <header className="flex justify-between items-center mb-6 border-b border-gray-700 pb-4">
                <h1 className="text-2xl font-bold">OMNI ChatOllama</h1>
                <select 
                    value={selectedModel} 
                    onChange={e => setSelectedModel(e.target.value)}
                    className="bg-gray-800 border border-gray-600 rounded p-2 text-white outline-none"
                >
                    {models.map(m => <option key={m} value={m}>{m}</option>)}
                </select>
            </header>

            <div className="flex-1 overflow-y-auto mb-6 space-y-4">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-3xl p-4 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-200'}`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
            </div>

            <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto w-full">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={`Message ${selectedModel}...`}
                    className="w-full bg-gray-800 border border-gray-600 rounded-lg py-4 px-6 text-white outline-none focus:border-blue-500 transition-colors"
                    disabled={isGenerating}
                />
                <button 
                    type="submit" 
                    className="absolute right-3 top-3 bg-blue-500 hover:bg-blue-400 text-white p-2 rounded-md transition-colors"
                    disabled={isGenerating}
                >
                    Send
                </button>
            </form>
        </div>
    );
};
