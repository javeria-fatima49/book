import React from 'react';
import UserRegistration from '../../components/UserRegistration';
import { AuthWrapper } from '../../contexts/AuthContext';

const SignUpPage: React.FC = () => {
  return (
    <AuthWrapper>
      <div className="container mx-auto py-12 flex justify-center">
        <UserRegistration />
      </div>
    </AuthWrapper>
  );
};

export default SignUpPage;