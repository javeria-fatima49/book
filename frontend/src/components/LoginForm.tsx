import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useForm } from 'react-hook-form';

interface LoginFormValues {
  email: string;
  password: string;
  rememberMe: boolean;
}

const LoginForm: React.FC = () => {
  const { signIn } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormValues>();

  const onSubmit = async (data: LoginFormValues) => {
    setError(null);
    setIsLoading(true);
    try {
      const result = await signIn(data.email, data.password);

      if (result.error) {
        // Handle different types of errors appropriately
        let errorMessage = result.error;

        // More specific error handling
        if (result.error.toLowerCase().includes('invalid credentials') ||
            result.error.toLowerCase().includes('password') ||
            result.error.toLowerCase().includes('email')) {
          errorMessage = 'Invalid email or password. Please check your credentials and try again.';
        } else if (result.error.toLowerCase().includes('network') || result.error.toLowerCase().includes('fetch')) {
          errorMessage = 'Network error. Please check your connection and try again.';
        } else if (result.error.toLowerCase().includes('timeout')) {
          errorMessage = 'Request timed out. Please try again.';
        } else if (result.error.toLowerCase().includes('not found')) {
          errorMessage = 'No account found with this email. Please check your email or sign up for a new account.';
        } else {
          errorMessage = `Login failed: ${result.error}. Please try again.`;
        }

        setError(errorMessage);
      } else {
        // Redirect to dashboard after successful login
        window.location.href = '/dashboard';
      }
    } catch (err: any) {
      // Handle network errors, server errors, etc.
      let errorMessage = 'An unexpected error occurred. Please try again.';

      if (err.message) {
        if (err.message.toLowerCase().includes('network') || err.message.toLowerCase().includes('fetch')) {
          errorMessage = 'Network error. Please check your connection and try again.';
        } else if (err.message.toLowerCase().includes('timeout')) {
          errorMessage = 'Request timed out. Please try again.';
        } else {
          errorMessage = `Login error: ${err.message}`;
        }
      }

      setError(errorMessage);
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-form-container">
      <div className="auth-form-header">
        <h1 className="auth-form-title">Welcome Back</h1>
        <p className="auth-form-subtitle">Sign in to your account to continue</p>
      </div>

      {error && (
        <div className="auth-form-error-message">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="auth-form">
        <div className="auth-form-fields">
          <div className="auth-form-fieldset">
            <label htmlFor="email" className="auth-form-label">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address'
                }
              })}
              className={`auth-input ${errors.email ? 'error' : ''}`}
              placeholder="you@example.com"
            />
            {errors.email && (
              <p className="auth-form-error">{errors.email.message}</p>
            )}
          </div>

          <div className="auth-form-fieldset">
            <div className="flex items-center justify-between mb-1">
              <label htmlFor="password" className="auth-form-label">
                Password
              </label>
              <a href="/auth/forgot-password" className="text-sm font-medium text-blue-600 hover:text-blue-500">
                Forgot password?
              </a>
            </div>
            <input
              id="password"
              type="password"
              {...register('password', {
                required: 'Password is required',
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters'
                }
              })}
              className={`auth-input ${errors.password ? 'error' : ''}`}
              placeholder="Enter your password"
            />
            {errors.password && (
              <p className="auth-form-error">{errors.password.message}</p>
            )}
          </div>
        </div>

        <div className="auth-checkbox-container">
          <input
            id="rememberMe"
            type="checkbox"
            {...register('rememberMe')}
            className="auth-checkbox"
          />
          <label htmlFor="rememberMe" className="auth-checkbox-label">
            Remember me
          </label>
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading}
            className={`auth-button auth-button-primary ${isLoading ? 'bg-blue-400 cursor-not-allowed' : ''}`}
          >
            {isLoading ? (
              <span className="flex items-center">
                <span className="spinner"></span>
                Signing in...
              </span>
            ) : (
              'Sign in'
            )}
          </button>
        </div>
      </form>

      <div className="auth-links">
        <p>
          Don't have an account?{' '}
          <a href="/auth/signup" className="auth-link">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
};

export default LoginForm;

