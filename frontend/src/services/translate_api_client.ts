export interface TranslateRequest {
  content: string;
  target_language: string;
  source_language?: string; // Assuming default to English
}

export interface TranslateResponse {
  translated_content: string;
}

// The actual API call function will be implemented in T017
export const translateContent = async (request: TranslateRequest, backendApiUrl: string): Promise<TranslateResponse> => {
  const response = await fetch(`${backendApiUrl}/api/v1/translate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to translate content.');
  }

  return response.json();
};