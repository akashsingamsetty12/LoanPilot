/**
 * Dashboard Page
 * ==================================
 * Application list with status cards, search, and filter by status.
 *
 * Features:
 *   - Search bar (filter by applicant name)
 *   - Filter chips: All / Created / Processing / Review / Decided
 *   - Grid of ApplicationCards: name, status, doc count, risk level, date
 *   - "New Application" button → /applications/new
 *
 * API calls:
 *   - listApplications({ status, page, limit })
 *
 * TODO: Implement the dashboard UI
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { listApplications } from '../api/applications';

export default function Dashboard() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch applications from API
  }, []);

  return (
    <div>
      <h1>LoanPilot Dashboard</h1>
      <p>Application list dashboard</p>
      <Link to="/applications/new">+ New Application</Link>
    </div>
  );
}
