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
    const mock = getMockAgentResponse(query);
    return {
      ...mock,
      response: mock.response,
      answer: mock.response,
    };
  }

  try {
    const response = await apiClient.post<any>(
      `/applications/${applicationId}/agent/query`,
      { question: query, query, application_id: applicationId }
    );
    const data = response.data;
    const text = data?.answer || data?.response || (typeof data === 'string' ? data : 'Analysis complete.');
    return {
      ...data,
      response: text,
      answer: text,
      sources: (data?.evidence || []).map((ev: any) => ({
        document: typeof ev === 'string' ? ev : (ev?.document || 'Document'),
        page: typeof ev === 'object' ? (ev?.page || 1) : 1
      }))
    };
  } catch (err) {
    console.warn('Agent API endpoint error, using fallback agent response:', err);
    await delay(800);
    const mock = getMockAgentResponse(query);
    return {
      ...mock,
      response: mock.response,
      answer: mock.response,
    };
  }
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
