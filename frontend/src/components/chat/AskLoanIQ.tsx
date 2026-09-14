import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Sparkles } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '../../types';
import { useAgent } from '../../hooks/useAgent';
import { Spinner } from '../ui/Spinner';

interface AskLoanIQProps {
  applicationId: string;
}

const suggestedQuestions = [
  'Why was this application flagged?',
  'Which documents are missing?',
  'Show me the income mismatch evidence.',
  'What is the recommendation?',
];

export function AskLoanIQ({ applicationId }: AskLoanIQProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { messages, loading, error, sendMessage } = useAgent(applicationId);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    setInput('');
    sendMessage(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Toggle button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-40 flex items-center gap-2.5 px-4 py-3 rounded-xl transition-all duration-200 hover:scale-105 active:scale-95"
          style={{
            background: '#AAFF00',
            color: '#0A0A0A',
            boxShadow: '0 0 24px rgba(170,255,0,0.3)',
          }}
          aria-label="Open LoanPilot AI Assistant"
        >
          <MessageSquare className="h-4 w-4" strokeWidth={2.5} />
          <span className="text-sm font-bold">Ask AI Agent</span>
        </button>
      )}

      {/* Chat panel */}
      {isOpen && (
        <div
          className="fixed bottom-6 right-6 z-40 w-[420px] h-[540px] rounded-2xl flex flex-col overflow-hidden shadow-2xl animate-fade-in"
          style={{
            background: '#111111',
            border: '1px solid rgba(255,255,255,0.08)',
            boxShadow: '0 24px 60px rgba(0,0,0,0.8), 0 0 20px rgba(170,255,0,0.06)',
          }}
        >
          {/* Header */}
          <div
            className="flex items-center justify-between px-5 py-3.5"
            style={{
              background: '#161616',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <div className="flex items-center gap-2.5">
              <div
                className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ background: 'rgba(170,255,0,0.12)', border: '1px solid rgba(170,255,0,0.25)' }}
              >
                <Sparkles className="h-3.5 w-3.5" style={{ color: '#AAFF00' }} />
              </div>
              <div>
                <h3 className="text-sm font-semibold" style={{ color: '#F0F0F0' }}>LoanPilot AI Agent</h3>
                <p className="text-[11px]" style={{ color: '#666666' }}>Document & Policy Verification Assistant</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded-lg transition-colors hover:bg-white/[0.06]"
              style={{ color: '#666666' }}
              aria-label="Close chat"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5">
            {messages.length === 0 && !loading && (
              <div className="space-y-4 my-auto py-4">
                <div className="text-center space-y-1">
                  <p className="text-sm font-medium" style={{ color: '#F0F0F0' }}>
                    Ask anything about this loan
                  </p>
                  <p className="text-xs" style={{ color: '#666666' }}>
                    Inspect income mismatches, missing files, or underwriting policy
                  </p>
                </div>
                <div className="space-y-1.5">
                  {suggestedQuestions.map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="w-full text-left px-3.5 py-2.5 text-xs rounded-lg transition-all duration-150 hover:border-white/20"
                      style={{
                        background: 'rgba(255,255,255,0.02)',
                        border: '1px solid rgba(255,255,255,0.06)',
                        color: '#A0A0A0',
                      }}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <ChatBubble key={msg.id} message={msg} />
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-xs py-2" style={{ color: '#666666' }}>
                <Spinner size="sm" />
                <span>Agent reviewing verification records...</span>
              </div>
            )}

            {error && (
              <div
                className="text-xs rounded-lg p-3"
                style={{
                  background: 'rgba(255,69,58,0.1)',
                  border: '1px solid rgba(255,69,58,0.2)',
                  color: '#FF453A',
                }}
              >
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div
            className="p-3"
            style={{
              background: '#141414',
              borderTop: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about discrepancies, policy, or borrower..."
                className="flex-1 text-xs rounded-lg px-3.5 py-2.5 transition-colors focus:outline-none focus:ring-1 focus:ring-[#AAFF00]/40"
                style={{
                  background: '#1C1C1C',
                  border: '1px solid rgba(255,255,255,0.08)',
                  color: '#F0F0F0',
                }}
                aria-label="Chat message input"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className="p-2.5 rounded-lg transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 flex-shrink-0"
                style={{
                  background: '#AAFF00',
                  color: '#0A0A0A',
                }}
                aria-label="Send message"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function ChatBubble({ message }: { message: ChatMessageType }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] px-3.5 py-2.5 rounded-xl text-xs leading-relaxed`}
        style={
          isUser
            ? {
                background: '#AAFF00',
                color: '#0A0A0A',
                fontWeight: 500,
              }
            : {
                background: '#1A1A1A',
                color: '#E0E0E0',
                border: '1px solid rgba(255,255,255,0.06)',
              }
        }
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
      </div>
    </div>
  );
}
