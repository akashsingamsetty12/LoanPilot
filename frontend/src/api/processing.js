/**
 * Processing API
 * ==================================
 * API calls for pipeline, classification, extraction, validation, verification.
 */

import api from './client';

const BASE = '/api/v1';

export const triggerPipeline = (appId) =>
  api.post(`${BASE}/applications/${appId}/process`);

export const getPipelineStatus = (appId) =>
  api.get(`${BASE}/applications/${appId}/pipeline-status`);

export const classifyDocument = (docId) =>
  api.post(`${BASE}/documents/${docId}/classify`);

export const extractFields = (docId) =>
  api.post(`${BASE}/documents/${docId}/extract`);

export const validateApplication = (appId) =>
  api.post(`${BASE}/applications/${appId}/validate`);

export const verifyApplication = (appId) =>
  api.post(`${BASE}/applications/${appId}/verify`);
