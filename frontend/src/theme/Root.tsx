import React from 'react';
import FloatingChatbot from '../components/FloatingChatbot';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

const Root: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { siteConfig } = useDocusaurusContext();

  // Get the backend API URL from site config
  // Using optional chaining to handle cases where customFields might not exist
  const backendApiUrl = (siteConfig.customFields?.backendApiUrl as string) || 'http://localhost:8000';

  return (
    <>
      {children}
      <FloatingChatbot backendApiUrl={backendApiUrl} />
    </>
  );
};

export default Root;