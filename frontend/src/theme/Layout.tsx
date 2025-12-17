import React, { ReactNode } from 'react';
import { useLocation } from '@docusaurus/router';
import OriginalLayout from '@theme-original/Layout';
import { AuthWrapper } from '../contexts/AuthContext';
import { PersonalizationProvider } from '../contexts/PersonalizationContext';

// Define the props for our custom layout (matching original Layout props)
interface LayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
  wrapperClassName?: string;
  searchMetadata?: {
    versionName?: string;
  };
  [key: string]: any; // Allow additional props
}

/**
 * Custom Layout component that wraps the original Docusaurus layout with providers
 */
const Layout: React.FC<LayoutProps> = (props) => {
  const location = useLocation();

  React.useEffect(() => {
    // Update document title when it changes
    if (props.title) {
      const suffix = ' | AI Book';
      document.title = props.title + suffix;
    }
  }, [props.title]);

  return (
    <OriginalLayout {...props}>
      {/* Providers wrapping the entire app */}
      <AuthWrapper>
        <PersonalizationProvider>
          {/* Render children (the actual page content) */}
          {props.children}
        </PersonalizationProvider>
      </AuthWrapper>
    </OriginalLayout>
  );
};

export default Layout;