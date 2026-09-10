/**
 * Risk API
 */

import api from './client';

const BASE = '/api/v1';

export const getFlags = (appId) =>
  api.get(`${BASE}/applications/${appId}/flags`);

export const assessRisk = (appId) =>
  api.post(`${BASE}/applications/${appId}/assess-risk`);
