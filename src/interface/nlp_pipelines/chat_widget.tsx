import React, { useState } from 'react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
}

export const ChatWidget: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;

    const userMsg: Message = { id: Date.now().toString(), text: input, sender: 'user' };
    setMessages(prev => [...prev, userMsg]);
    setInput('');

    // Deterministic mock response based on length
    setTimeout(() => {
      const responseText = userMsg.text.length > 20 
        ? "That's quite detailed. Let me process that intent via our Omni vector pipeline."
        : "Acknowledged. What else can I help you with?";
      
      const botMsg: Message = { id: (Date.now() + 1).toString(), text: responseText, sender: 'bot' };
      setMessages(prev => [...prev, botMsg]);
    }, 500);
  };

  return (
    <div className="w-80 h-96 flex flex-col bg-white rounded-lg shadow-xl overflow-hidden border border-gray-200">
      <div className="bg-blue-600 text-white px-4 py-3 font-semibold flex justify-between items-center">
        <span>OmniNLP Assistant</span>
        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map(m => (
          <div key={m.id} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
              m.sender === 'user' ? 'bg-blue-500 text-white rounded-br-none' : 'bg-gray-200 text-gray-800 rounded-bl-none'
            }`}>
              {m.text}
            </div>
          </div>
        ))}
        {messages.length === 0 && (
          <div className="text-center text-gray-400 text-sm mt-10">Start a conversation...</div>
        )}
      </div>

      <div className="p-3 bg-white border-t border-gray-200 flex">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a message..."
          className="flex-1 text-sm outline-none px-2 py-1 bg-gray-100 rounded-l focus:bg-white border border-transparent focus:border-blue-400 transition"
        />
        <button 
          onClick={handleSend}
          className="bg-blue-600 text-white px-3 text-sm rounded-r hover:bg-blue-700 transition"
        >
          Send
        </button>
      </div>
    </div>
  );
};
