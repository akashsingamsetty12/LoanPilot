/**
 * Report View Page
 * =====================================
 * Displays the generated verification report with PDF download.
 *
 * Sections:
 *   1. Applicant Information
 *   2. Document Summary
 *   3. Verification Results
 *   4. Risk & Flags
 *   5. Recommendation
 *
 * API calls:
 *   - getReport(appId) → ReportResponse
 *   - getReportDownloadUrl(appId) → PDF download link
 *
 * TODO: Implement the report view
 */

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getReport, getReportDownloadUrl } from '../api/agent';

export default function ReportView() {
  const { id } = useParams();
  const [report, setReport] = useState(null);

  useEffect(() => {
    // TODO: Fetch report data
  }, [id]);

  return (
    <div>
      <h1>Verification Report: {id}</h1>
      <p>Verification Report and PDF download</p>
      <a href={getReportDownloadUrl(id)} download>
        Download PDF
      </a>
    </div>
  );
}
