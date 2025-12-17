export interface AgentRequest {
  skills: string[];
  input_data: Record<string, any>;
  config?: Record<string, any>;
}

export interface AgentResult {
  skill: string;
  result: {
    status: string;
    data: any;
    metadata?: Record<string, any>;
  };
}

export interface AgentResponse {
  results: AgentResult[];
  status: string;
  execution_time: number;
}

/**
 * Calls the agent orchestration API to execute one or more skills.
 * 
 * @param {AgentRequest} request - The request object containing skills to execute and input data
 * @param {string} backendApiUrl - The base URL for the backend API
 * @returns {Promise<AgentResponse>} The response from the agent orchestration
 */
export const queryAgent = async (
  request: AgentRequest,
  backendApiUrl: string
): Promise<AgentResponse> => {
  const response = await fetch(`${backendApiUrl}/api/v1/agents/orchestrate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to execute agent skills');
  }

  return response.json();
};