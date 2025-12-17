import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { AuthWrapper } from '../contexts/AuthContext';

const DashboardPage: React.FC = () => {
  const { user, loading } = useAuth();

  return (
    <div className="dashboard-container">
      <div className="dashboard-card">
        <h1 className="dashboard-title">Dashboard</h1>

        {loading ? (
          <p>Loading...</p>
        ) : user ? (
          <div>
            <p className="text-lg mb-4">Welcome, {user.email}!</p>
            <p>You are now signed in to your account.</p>
            {user.firstName && user.lastName && (
              <p className="text-md mb-2">Name: {user.firstName} {user.lastName}</p>
            )}

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <a
                href="/"
                className="auth-button auth-button-primary"
              >
                Go to Homepage
              </a>
              <a
                href="/docs"
                className="auth-button auth-button-secondary"
              >
                Read Documentation
              </a>
            </div>
          </div>
        ) : (
          <div>
            <p>You need to be signed in to access the dashboard.</p>
            <div className="mt-4">
              <a
                href="/auth/signin"
                className="auth-button auth-button-primary"
              >
                Sign In
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Wrap the component with AuthWrapper
const WrappedDashboardPage: React.FC = () => {
  return (
    <AuthWrapper>
      <DashboardPage />
    </AuthWrapper>
  );
};

export default WrappedDashboardPage;