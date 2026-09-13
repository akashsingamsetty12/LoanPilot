/**
 * Application Review Page
 * ===========================================================
 * Full review dashboard for a single loan application.
 *
 * Layout:
 *   Top bar:     Application ID, status badge, risk gauge
 *   Tab 1:       Documents — DocumentCards grid (type, status, confidence)
 *   Tab 2:       Extracted Fields — FieldTable per document with confidence bars
 *   Tab 3:       Verification — VerificationTable (matches ✓, mismatches ✗)
 *   Tab 4:       Risk & Flags — FlagList sorted by severity, risk score gauge
 *   Side panel:  ChatPanel ("Ask LoanPilot") — always visible on right
 *   Bottom bar:  Decision buttons (Approve / Reject / Request More Info) + Notes
 *
 * KEY RULE: Every number and flag should be clickable → shows source document + page evidence
 *
 * API calls:
 *   - getApplication(appId) → full state
 *   - getFlags(appId)
 *   - askLoanPilot(appId, question)
 *   - decideApplication(appId, decision)
 *
 * TODO: Implement the review dashboard
 */

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getApplication } from '../api/applications';
import ChatPanel from '../components/agent/ChatPanel';

export default function ApplicationReview() {
  const { id } = useParams();
  const [application, setApplication] = useState(null);
  const [activeTab, setActiveTab] = useState('documents');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch application data
  }, [id]);

  return (
    <div className="flex gap-4 h-[calc(100vh-100px)] p-4">
      <div className="flex-1 flex flex-col overflow-auto">
        <h1 className="text-xl font-bold text-gray-900">Application Review: {id}</h1>
        <p className="text-sm text-gray-500">Application review dashboard</p>

        {/* Tab navigation */}
        <nav className="flex gap-2 border-b my-3">
          {['documents', 'extraction', 'verification', 'risk'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1.5 text-sm font-medium border-b-2 ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </nav>

        {/* Tab content */}
        <div className="flex-1 overflow-auto">
          {activeTab === 'documents' && <p className="text-sm text-gray-500 p-4">Document cards grid</p>}
          {activeTab === 'extraction' && <p className="text-sm text-gray-500 p-4">Extracted fields table</p>}
          {activeTab === 'verification' && <p className="text-sm text-gray-500 p-4">Verification comparison table</p>}
          {activeTab === 'risk' && <p className="text-sm text-gray-500 p-4">Risk gauge and flag cards</p>}
        </div>
      </div>

      {/* Chat panel — always visible on right */}
      <aside className="w-96 h-full flex-shrink-0">
        <ChatPanel appId={id} />
      </aside>
    </div>
  );
}
