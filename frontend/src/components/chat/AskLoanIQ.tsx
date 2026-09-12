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
          className="fixed bottom-6 right-6 z-40 flex items-center gap-2 bg-primary-600 text-white px-4 py-3 rounded-lg shadow-lg hover:bg-primary-700 transition-colors"
          aria-label="Open LoanIQ Assistant"
        >
          <MessageSquare className="h-5 w-5" />
          <span className="text-sm font-medium">Ask LoanIQ</span>
        </button>
      )}

      {/* Chat panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-40 w-[400px] h-[520px] bg-white border border-surface-300 rounded-lg shadow-dropdown flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-surface-300 bg-surface-50">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary-600" />
              <div>
                <h3 className="text-sm font-semibold text-charcoal">Ask LoanIQ</h3>
                <p className="text-xs text-charcoal-muted">AI-powered application assistant</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded hover:bg-surface-200 text-charcoal-muted transition-colors"
              aria-label="Close chat"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && !loading && (
              <div className="space-y-3">
                <p className="text-sm text-charcoal-muted text-center py-2">
                  Ask questions about this application.
                </p>
                <div className="space-y-1.5">
                  {suggestedQuestions.map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="w-full text-left px-3 py-2 text-xs text-charcoal-secondary bg-surface-50 border border-surface-200 rounded-md hover:bg-surface-100 transition-colors"
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
              <div className="flex items-center gap-2 text-sm text-charcoal-muted">
                <Spinner size="sm" />
                <span>Thinking...</span>
              </div>
            )}

            {error && (
              <div className="text-xs text-risk-high bg-risk-high-bg border border-risk-high-border rounded px-3 py-2">
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-surface-300 p-3">
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about this application..."
                className="input-field resize-none min-h-[40px] max-h-[80px]"
                rows={1}
                aria-label="Chat message input"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className="p-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
                aria-label="Send message"
              >
                <Send className="h-4 w-4" />
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
        className={`max-w-[85%] px-3 py-2 rounded-lg text-sm ${
          isUser
            ? 'bg-primary-600 text-white'
            : 'bg-surface-100 text-charcoal border border-surface-200'
        }`}
      >
        <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
      </div>
    </div>
  );
}
