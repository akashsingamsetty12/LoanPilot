/**
 * Documents API
 * =================================
 * API calls for document upload and status tracking.
 */

import api from './client';

const BASE = '/api/v1';

export const uploadDocuments = (appId, files) => {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  return api.post(`${BASE}/applications/${appId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const listDocuments = (appId) =>
  api.get(`${BASE}/applications/${appId}/documents`);

export const getDocument = (docId) =>
  api.get(`${BASE}/documents/${docId}`);

export const getDocumentStatus = (docId) =>
  api.get(`${BASE}/documents/${docId}/status`);
