import React, { useState, useRef, useEffect } from 'react';
import { translateContent } from '../services/translate_api_client';

/**
 * Props for the UrduTranslateButton component.
 */
interface UrduTranslateButtonProps {
  /** The base URL for the backend API. */
  backendApiUrl: string;
}

/**
 * A React functional component that provides a button to translate the main content
 * of a Docusaurus page to Urdu and switch back to the original language.
 * It manages the translation state, calls the backend API, and handles content replacement.
 *
 * @param {UrduTranslateButtonProps} { backendApiUrl } - The props for the component, including the backend API URL.
 */
const UrduTranslateButton: React.FC<UrduTranslateButtonProps> = ({ backendApiUrl }) => {
  /** @type {boolean} isTranslated - State to track whether the content is currently translated to Urdu. */
  const [isTranslated, setIsTranslated] = useState<boolean>(false);
  /** @type {boolean} loading - State to indicate if a translation request is currently in progress. */
  const [loading, setLoading] = useState<boolean>(false);
  /** @type {string | null} error - State to store any error message that occurs during translation. */
  const [error, setError] = useState<string | null>(null);
  /** @type {React.MutableRefObject<string | null>} originalContentRef - Ref to store the original HTML content of the main Docusaurus page. */
  const originalContentRef = useRef<string | null>(null);
  const mainContentElementId = 'docusaurus-main-content'; // ID of the main content area

  // Store original content on first render
  useEffect(() => {
    const mainContentElement = document.getElementById(mainContentElementId);
    if (mainContentElement && originalContentRef.current === null) {
      originalContentRef.current = mainContentElement.innerHTML;
    }
  }, []);

  /**
   * Handles the click event for the translate button.
   * Toggles between original and translated content, manages loading, and calls the backend API.
   */
  const handleTranslate = async () => {
    setLoading(true);
    setError(null);
    const mainContentElement = document.getElementById(mainContentElementId);

    if (!mainContentElement) {
      setError('Main content element not found.');
      setLoading(false);
      return;
    }

    try {
      if (!isTranslated) {
        // Translate to Urdu
        const contentToTranslate = originalContentRef.current || mainContentElement.innerHTML;
        const targetLanguage = "ur"; // Urdu

        const response = await translateContent(
          { content: contentToTranslate, target_language: targetLanguage },
          backendApiUrl
        );
        mainContentElement.innerHTML = response.translated_content; // Replace with translated content
        setIsTranslated(true);
      } else {
        // Revert to original content
        if (originalContentRef.current) {
          mainContentElement.innerHTML = originalContentRef.current;
        }
        setIsTranslated(false);
      }
    } catch (err: any) {
      console.error('Error translating content:', err);
      setError(err.message || 'Failed to translate content.');
      // Revert to original content on error if it was translated
      if (isTranslated && originalContentRef.current) {
        mainContentElement.innerHTML = originalContentRef.current;
        setIsTranslated(false);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleTranslate} disabled={loading}>
      {loading ? 'Translating...' : (isTranslated ? 'Show Original' : 'Translate to Urdu')}
      {error && <span style={{ color: 'red', marginLeft: '10px' }}>{error}</span>}
    </button>
  );
};

export default UrduTranslateButton;
