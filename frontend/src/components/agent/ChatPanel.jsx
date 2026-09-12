/**
 * ChatPanel — "Ask LoanPilot" AI Investigation Agent interface.
 * Features:
 *   - Interactive chat message list (Officer questions + Agent responses)
 *   - Collapsible "Agent Reasoning" drawer displaying the step-by-step trace
 *   - Evidence cards highlighting source document, page, and extracted values
 *   - Policy references and prominent "Human Review Required" status badges
 */

import { useState } from 'react';
import { askLoanPilot } from '../../api/agent';

export default function ChatPanel({ appId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [openTraceStep, setOpenTraceStep] = useState(null);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userQuestion = input.trim();
    setInput('');

    // Add user message to UI state immediately
    const userMsgObj = { id: Date.now(), role: 'user', content: userQuestion };
    setMessages((prev) => [...prev, userMsgObj]);
    setLoading(true);

    try:
      const response = await askLoanPilot(appId, userQuestion);
      const data = response.data;

      const agentMsgObj = {
        id: Date.now() + 1,
        role: 'agent',
        answer: data.answer,
        risk_level: data.risk_level,
        evidence: data.evidence || [],
        policy_reference: data.policy_reference,
        recommendation: data.recommendation,
        requires_human_review: data.requires_human_review,
        trace: data.trace || [],
      };

      setMessages((prev) => [...prev, agentMsgObj]);
    } catch (err) {
      console.error('Failed to send question to LoanPilot Agent:', err);
      const errorMsgObj = {
        id: Date.now() + 1,
        role: 'agent',
        answer: 'Sorry, an error occurred while connecting to the investigation agent.',
        requires_human_review: true,
        trace: [],
      };
      setMessages((prev) => [...prev, errorMsgObj]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border rounded-lg flex flex-col h-full bg-white shadow-sm">
      {/* Panel Header */}
      <div className="p-3 border-b bg-blue-50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">🤖</span>
          <div>
            <h3 className="font-semibold text-blue-900 text-sm">Ask LoanPilot — AI Investigation Agent</h3>
            <p className="text-xs text-blue-600">Multi-Turn Tool Orchestration & Policy RAG</p>
          </div>
        </div>
        <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full font-medium">
          Human-in-the-Loop Safeguard Enabled
        </span>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <p className="text-sm font-medium text-gray-500">Ask a question about this application...</p>
            <div className="mt-3 flex flex-wrap gap-2 justify-center text-xs">
              <button
                onClick={() => setInput('Why was this application flagged?')}
                className="px-2.5 py-1 bg-gray-100 hover:bg-blue-50 text-gray-700 rounded border"
              >
                "Why was this application flagged?"
              </button>
              <button
                onClick={() => setInput('What does policy say about income mismatches?')}
                className="px-2.5 py-1 bg-gray-100 hover:bg-blue-50 text-gray-700 rounded border"
              >
                "What does policy say about income mismatches?"
              </button>
              <button
                onClick={() => setInput('Show me evidence for the income discrepancy')}
                className="px-2.5 py-1 bg-gray-100 hover:bg-blue-50 text-gray-700 rounded border"
              >
                "Show me evidence for the income discrepancy"
              </button>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg p-3 text-sm ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-gray-50 border border-gray-200 text-gray-900 rounded-bl-none'
              }`}
            >
              {msg.role === 'user' ? (
                <p>{msg.content}</p>
              ) : (
                <div className="space-y-3">
                  {/* Primary Answer */}
                  <p className="text-gray-800 leading-relaxed">{msg.answer}</p>

                  {/* Human Review & Risk Level Badges */}
                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    {msg.requires_human_review && (
                      <span className="px-2 py-0.5 text-xs bg-amber-100 text-amber-800 border border-amber-300 rounded font-medium">
                        ⚠️ Human Review Required
                      </span>
                    )}
                    {msg.risk_level && (
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded ${
                          msg.risk_level === 'HIGH'
                            ? 'bg-red-100 text-red-800'
                            : msg.risk_level === 'MEDIUM'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        Risk Level: {msg.risk_level}
                      </span>
                    )}
                  </div>

                  {/* Evidence Cards */}
                  {msg.evidence && msg.evidence.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <h4 className="text-xs font-semibold text-gray-700 mb-1.5 flex items-center gap-1">
                        <span>📄</span> Supporting Evidence ({msg.evidence.length})
                      </h4>
                      <div className="space-y-1.5">
                        {msg.evidence.map((item, idx) => (
                          <div key={idx} className="bg-white p-2 border rounded text-xs space-y-0.5">
                            <div className="flex justify-between font-medium text-gray-700">
                              <span>Doc: {item.document}</span>
                              <span className="text-gray-500">Page {item.page}</span>
                            </div>
                            <p className="text-gray-600 text-xs italic">{item.value}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Policy Reference */}
                  {msg.policy_reference && (
                    <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs">
                      <span className="font-semibold text-blue-900">📚 Policy Guidance:</span>{' '}
                      <span className="text-blue-800">{msg.policy_reference}</span>
                    </div>
                  )}

                  {/* Agent Reasoning Drawer */}
                  {msg.trace && msg.trace.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-gray-200">
                      <button
                        onClick={() =>
                          setOpenTraceStep(openTraceStep === msg.id ? null : msg.id)
                        }
                        className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1"
                      >
                        <span>🧠</span> Agent Reasoning Trace ({msg.trace.length} tool calls){' '}
                        <span>{openTraceStep === msg.id ? '▲' : '▼'}</span>
                      </button>

                      {openTraceStep === msg.id && (
                        <div className="mt-2 space-y-1.5 bg-gray-100 p-2.5 rounded text-xs">
                          {msg.trace.map((tStep) => (
                            <div key={tStep.step} className="bg-white p-2 border rounded">
                              <div className="flex justify-between items-center font-medium text-gray-700">
                                <span>Step {tStep.step}: {tStep.tool}</span>
                              </div>
                              <p className="text-gray-600 mt-0.5">{tStep.summary}</p>
                              {tStep.args && Object.keys(tStep.args).length > 0 && (
                                <p className="text-[10px] text-gray-400 font-mono mt-1">
                                  args: {JSON.stringify(tStep.args)}
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-gray-500 py-2">
            <span className="animate-spin text-base">⚙️</span> LoanPilot Agent is analyzing tools and policies...
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="p-3 border-t bg-gray-50 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about flags, evidence, or lending policy..."
          className="flex-1 border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium rounded-md text-sm transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
