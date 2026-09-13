import apiClient from './client';
import type { AgentResponse } from '../types';
import { getMockAgentResponse } from '../mock/data';

const useMock = import.meta.env.VITE_USE_MOCK === 'true';

export async function queryAgent(
  applicationId: string,
  query: string
): Promise<AgentResponse> {
  if (useMock) {
    await delay(1200);
    return getMockAgentResponse(query);
  }

  const response = await apiClient.post<AgentResponse>(
    `/applications/${applicationId}/agent/query`,
    { query, application_id: applicationId }
  );
  return response.data;
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
