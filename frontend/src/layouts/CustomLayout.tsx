import React, { ReactNode } from 'react';
import { useLocation } from '@docusaurus/router';
import Layout from '@theme/Layout'; // Import the default Docusaurus layout
import { AuthWrapper } from '../contexts/AuthContext';
import { PersonalizationProvider } from '../contexts/PersonalizationContext';
import FloatingChatbot from '../components/FloatingChatbot';

// Define the props for our custom layout
interface CustomLayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
  hideNavbar?: boolean;
  hideFooter?: boolean;
  className?: string;
}

/**
 * Custom layout component that wraps pages with providers and UI elements
 */
const CustomLayout: React.FC<CustomLayoutProps> = ({
  children,
  title,
  description,
  hideNavbar = false,
  hideFooter = false,
  className,
  ...props
}) => {
  const location = useLocation();

  React.useEffect(() => {
    // Update document title when it changes
    if (title) {
      document.title = `${title} | AI Book`;
    }
  }, [title]);

  return (
    <Layout
      wrapperClassName={className}
      title={title}
      description={description}
      {...props}
    >
      {/* Providers wrapping the entire app */}
      <AuthWrapper>
        <PersonalizationProvider>
          {/* Main Content - Layout handles Navbar/Footer */}
          <main className="custom-layout-main">
            {children}
          </main>

          {/* Floating Chatbot - Always visible regardless of page */}
          <FloatingChatbot
            backendApiUrl={process.env.REACT_APP_BACKEND_API_URL || 'http://localhost:8000'}
            bookTitle="Physical AI & Humanoid Robotics"
            bookAuthor="AI Assistant"
          />
        </PersonalizationProvider>
      </AuthWrapper>
    </Layout>
  );
};

export default CustomLayout;