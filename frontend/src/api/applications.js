/**
 * Applications API
 * ====================================
 * API calls for loan application CRUD operations.
 */

import api from './client';

const BASE = '/api/v1';

export const createApplication = (data) =>
  api.post(`${BASE}/applications`, data);

export const listApplications = (params = {}) =>
  api.get(`${BASE}/applications`, { params });

export const getApplication = (appId) =>
  api.get(`${BASE}/applications/${appId}`);

export const decideApplication = (appId, decision) =>
  api.patch(`${BASE}/applications/${appId}/decide`, decision);
