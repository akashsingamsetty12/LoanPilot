/**
 * Agent API
 * "Ask LoanPilot" chatbot and report endpoints.
 */

import api from './client';

const BASE = '/api/v1';

export const askLoanPilot = (appId, question, conversationId = null) =>
  api.post(`${BASE}/applications/${appId}/agent`, {
    question,
    conversation_id: conversationId,
  });

export const getReport = (appId) =>
  api.get(`${BASE}/applications/${appId}/report`);

export const generateReport = (appId) =>
  api.post(`${BASE}/applications/${appId}/report/generate`);

export const getReportDownloadUrl = (appId) =>
  `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${BASE}/applications/${appId}/report/download`;
