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

export default function ApplicationReview() {
  const { id } = useParams();
  const [application, setApplication] = useState(null);
  const [activeTab, setActiveTab] = useState('documents');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch application data
  }, [id]);

  return (
    <div>
      <h1>Application Review: {id}</h1>
      <p>Application review dashboard</p>

      {/* Tab navigation */}
      <nav>
        {['documents', 'extraction', 'verification', 'risk'].map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)}>
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </nav>

      {/* Tab content */}
      <div>
        {activeTab === 'documents' && <p>TODO: Document cards grid</p>}
        {activeTab === 'extraction' && <p>TODO: Extracted fields table</p>}
        {activeTab === 'verification' && <p>TODO: Verification comparison table</p>}
        {activeTab === 'risk' && <p>TODO: Risk gauge and flag cards</p>}
      </div>

      {/* Chat panel — always visible */}
      <aside>
        <p>TODO: "Ask LoanPilot" chat panel</p>
      </aside>
    </div>
  );
}
