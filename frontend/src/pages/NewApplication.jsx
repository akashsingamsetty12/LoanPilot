/**
 * New Application Page
 * ========================================
 * Create a new application and upload documents.
 *
 * Features:
 *   - Applicant Name input
 *   - Drag-and-drop zone: PDF, JPG, PNG (max 10MB each)
 *   - File list with remove buttons
 *   - Upload progress bars per file
 *   - "Create & Process" button → API → redirect to review
 *
 * API calls:
 *   - createApplication({ applicant_name })
 *   - uploadDocuments(appId, files)
 *   - triggerPipeline(appId)
 *
 * TODO: Implement the upload UI
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createApplication } from '../api/applications';
import { uploadDocuments } from '../api/documents';
import { triggerPipeline } from '../api/processing';

export default function NewApplication() {
  const navigate = useNavigate();
  const [applicantName, setApplicantName] = useState('');
  const [files, setFiles] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // TODO: Implement create + upload + process flow
  };

  return (
    <div>
      <h1>New Loan Application</h1>
      <p>Application creation and document upload</p>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Applicant Name"
          value={applicantName}
          onChange={(e) => setApplicantName(e.target.value)}
        />
        {/* TODO: Add drag-and-drop file upload component */}
        <button type="submit">Create & Process</button>
      </form>
    </div>
  );
}
