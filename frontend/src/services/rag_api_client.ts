export interface Source {
  text: string;
  metadata: Record<string, unknown>;
}

export interface RagQueryRequest {
  query: string;
  user_id?: string;
}

export interface RagQueryResponse {
  answer: string;
  sources: Source[];
}

export const queryRag = async (
  request: RagQueryRequest,
  backendApiUrl: string,
): Promise<RagQueryResponse> => {
  const response = await fetch(`${backendApiUrl}/api/v1/rag/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch RAG response');
  }

  return response.json();
};
