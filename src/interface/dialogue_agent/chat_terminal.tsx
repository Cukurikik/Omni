import React, { useState } from 'react';

interface Message {
  role: 'user' | 'agent';
  content: string;
}

export const ChatTerminal: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input) return;

    const newMsgs: Message[] = [...messages, { role: 'user', content: input }];
    setMessages(newMsgs);
    setInput('');

    // Deterministic response logic based on input length
    setTimeout(() => {
      const responseCode = input.length * 42;
      setMessages([...newMsgs, { 
        role: 'agent', 
        content: `Acknowledged. Generated response code: ${responseCode}` 
      }]);
    }, 500);
  };

  return (
    <div className="flex flex-col h-96 max-w-lg mx-auto border border-gray-300 rounded overflow-hidden font-sans">
      <div className="bg-blue-600 text-white px-4 py-2 font-bold">
        DialoGPT Agent Node
      </div>
      
      <div className="flex-1 bg-gray-50 p-4 overflow-y-auto flex flex-col gap-3">
        {messages.map((msg, i) => (
          <div key={i} className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white self-end' : 'bg-gray-200 text-gray-800 self-start'}`}>
            {msg.content}
          </div>
        ))}
      </div>

      <form onSubmit={handleSend} className="p-3 bg-white border-t border-gray-300 flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Type message..."
        />
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Send
        </button>
      </form>
    </div>
  );
};
