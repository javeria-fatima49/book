import React from 'react';
import LoginForm from '../../components/LoginForm';
import { AuthWrapper } from '../../contexts/AuthContext';

const SignInPage: React.FC = () => {
  return (
    <AuthWrapper>
      <div className="container mx-auto py-12 flex justify-center">
        <LoginForm />
      </div>
    </AuthWrapper>
  );
};

export default SignInPage;