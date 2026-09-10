/**
 * ChatPanel — "Ask LoanPilot" chat interface.""" *
 * Features:
 *   - Message list (user questions + agent answers)
 *   - Text input + send button
 *   - Shows evidence and sources with each answer
 *   - Suggested follow-up questions
 *
 * API: askLoanPilot(appId, question)
 */

import { useState } from 'react';
import { askLoanPilot } from '../../api/agent';

export default function ChatPanel({ appId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    // TODO: Implement chat send + display
  };

  return (
    <div className="border rounded-lg flex flex-col h-full">
      <div className="p-3 border-b bg-blue-50">
        <h3 className="font-medium text-blue-700">🤖 Ask LoanPilot</h3>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-3 space-y-3">
        {messages.length === 0 && (
          <p className="text-sm text-gray-400">Ask a question about this application...</p>
        )}
        {/* TODO: Render message bubbles with evidence */}
      </div>

      {/* Input */}
      <div className="p-3 border-t flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Why was this flagged?"
          className="flex-1 border rounded px-3 py-2 text-sm"
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend} className="px-4 py-2 bg-blue-600 text-white rounded text-sm">
          Send
        </button>
      </div>
    </div>
  );
}
