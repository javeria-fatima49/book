import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useForm } from 'react-hook-form';

interface RegistrationFormData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  developerLevel: 'beginner' | 'intermediate' | 'advanced';
  roboticsInterests: string;
  programmingLanguages: string;
  yearsExperience: number;
  learningGoals: string;
  preferredAiModel: 'openai' | 'gemini' | 'chatkit';
}

const UserRegistration: React.FC = () => {
  const { signUp } = useAuth();
  const [registrationStep, setRegistrationStep] = useState<number>(1); // Multi-step form
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, formState: { errors }, watch, setValue } = useForm<RegistrationFormData>();

  const onSubmit = async (data: RegistrationFormData) => {
    try {
      setError(null);
      setIsLoading(true);

      // Sign up with basic info and background data
      const result = await signUp(
        data.email,
        data.password,
        data.firstName,
        data.lastName,
        {
          developerLevel: data.developerLevel,
          roboticsInterests: data.roboticsInterests,
          programmingLanguages: data.programmingLanguages,
          yearsExperience: data.yearsExperience,
          learningGoals: data.learningGoals,
          preferredAiModel: data.preferredAiModel
        }
      );

      if (result.error) {
        // Handle different types of errors appropriately
        let errorMessage = result.error;

        // More specific error handling
        if (result.error.toLowerCase().includes('already exists')) {
          errorMessage = 'A user with this email already exists. Please try logging in instead.';
        } else if (result.error.toLowerCase().includes('password')) {
          errorMessage = 'Password does not meet requirements. Please ensure it has at least 8 characters with numbers and letters.';
        } else if (result.error.toLowerCase().includes('email')) {
          errorMessage = 'Invalid email format. Please enter a valid email address.';
        } else if (result.error.toLowerCase().includes('network') || result.error.toLowerCase().includes('fetch')) {
          errorMessage = 'Network error. Please check your connection and try again.';
        } else if (result.error.toLowerCase().includes('timeout')) {
          errorMessage = 'Request timed out. Please try again.';
        } else {
          errorMessage = `Registration failed: ${result.error}. Please try again.`;
        }

        setError(errorMessage);
        return;
      }

      // Log registration data for debugging
      console.log('Registration data stored:', {
        developerLevel: data.developerLevel,
        roboticsInterests: data.roboticsInterests,
        programmingLanguages: data.programmingLanguages,
        yearsExperience: data.yearsExperience,
        learningGoals: data.learningGoals,
        preferredAiModel: data.preferredAiModel
      });

      // Wait a bit to ensure the auth state is updated
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Now redirect to dashboard after ensuring auth state is updated
      window.location.href = '/dashboard';
    } catch (err: any) {
      // Handle network errors, server errors, etc.
      let errorMessage = 'An unexpected error occurred during registration. Please try again.';

      if (err.message) {
        if (err.message.toLowerCase().includes('network') || err.message.toLowerCase().includes('fetch')) {
          errorMessage = 'Network error. Please check your connection and try again.';
        } else if (err.message.toLowerCase().includes('timeout')) {
          errorMessage = 'Request timed out. Please try again.';
        } else {
          errorMessage = `Registration error: ${err.message}`;
        }
      }

      setError(errorMessage);
      console.error('Registration error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Multi-step form for background collection
  const renderStep = () => {
    switch(registrationStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Account Information</h2>
              <p className="text-sm text-gray-600">Let's start with your basic information</p>
            </div>

            <div className="space-y-4">
              <div className="auth-form-fieldset">
                <label htmlFor="firstName" className="auth-form-label">
                  First Name
                </label>
                <input
                  id="firstName"
                  {...register('firstName', {
                    required: 'First name is required',
                    minLength: {
                      value: 2,
                      message: 'First name must be at least 2 characters'
                    },
                    maxLength: {
                      value: 50,
                      message: 'First name is too long'
                    }
                  })}
                  className={`auth-input ${errors.firstName ? 'error' : ''}`}
                  placeholder="John"
                />
                {errors.firstName && (
                  <p className="auth-form-error">{errors.firstName.message}</p>
                )}
              </div>

              <div className="auth-form-fieldset">
                <label htmlFor="lastName" className="auth-form-label">
                  Last Name
                </label>
                <input
                  id="lastName"
                  {...register('lastName', {
                    required: 'Last name is required',
                    minLength: {
                      value: 2,
                      message: 'Last name must be at least 2 characters'
                    },
                    maxLength: {
                      value: 50,
                      message: 'Last name is too long'
                    }
                  })}
                  className={`auth-input ${errors.lastName ? 'error' : ''}`}
                  placeholder="Doe"
                />
                {errors.lastName && (
                  <p className="auth-form-error">{errors.lastName.message}</p>
                )}
              </div>

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
                <label htmlFor="password" className="auth-form-label">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 8,
                      message: 'Password must be at least 8 characters'
                    },
                    maxLength: {
                      value: 128,
                      message: 'Password is too long'
                    },
                    validate: {
                      hasNumber: (value) => /\d/.test(value) || 'Password must contain at least one number',
                      hasUppercase: (value) => /[A-Z]/.test(value) || 'Password must contain at least one uppercase letter',
                      hasLowercase: (value) => /[a-z]/.test(value) || 'Password must contain at least one lowercase letter',
                      hasSpecialChar: (value) => /[^A-Za-z0-9]/.test(value) || 'Password must contain at least one special character'
                    }
                  })}
                  className={`auth-input ${errors.password ? 'error' : ''}`}
                  placeholder="At least 8 characters, with numbers and letters"
                />
                {errors.password && (
                  <p className="auth-form-error">{errors.password.message}</p>
                )}
              </div>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Technical Background</h2>
              <p className="text-sm text-gray-600">Help us understand your experience</p>
            </div>

            <div className="space-y-4">
              <div className="auth-form-fieldset">
                <label htmlFor="developerLevel" className="auth-form-label">
                  Developer Level
                </label>
                <select
                  id="developerLevel"
                  {...register('developerLevel')}
                  className="auth-input"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div className="auth-form-fieldset">
                <label htmlFor="yearsExperience" className="auth-form-label">
                  Years of Experience
                </label>
                <input
                  id="yearsExperience"
                  type="number"
                  min="0"
                  max="50"
                  {...register('yearsExperience', { valueAsNumber: true, min: 0, max: 50 })}
                  className="auth-input"
                  placeholder="0"
                />
              </div>

              <div className="auth-form-fieldset">
                <label htmlFor="programmingLanguages" className="auth-form-label">
                  Programming Languages
                </label>
                <input
                  id="programmingLanguages"
                  {...register('programmingLanguages', {
                    maxLength: {
                      value: 200,
                      message: 'Programming languages list is too long'
                    }
                  })}
                  className="auth-input"
                  placeholder="Comma-separated: Python, JavaScript, C++, etc."
                />
                {errors.programmingLanguages && (
                  <p className="auth-form-error">{errors.programmingLanguages.message}</p>
                )}
              </div>
            </div>
          </div>
        );
      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Learning Goals</h2>
              <p className="text-sm text-gray-600">What are you hoping to achieve?</p>
            </div>

            <div className="space-y-4">
              <div className="auth-form-fieldset">
                <label htmlFor="roboticsInterests" className="auth-form-label">
                  Robotics Interests
                </label>
                <textarea
                  id="roboticsInterests"
                  {...register('roboticsInterests', {
                    maxLength: {
                      value: 500,
                      message: 'Robotics interests description is too long'
                    }
                  })}
                  className="auth-input"
                  rows={3}
                  placeholder="What aspects of robotics interest you most?"
                />
                {errors.roboticsInterests && (
                  <p className="auth-form-error">{errors.roboticsInterests.message}</p>
                )}
              </div>

              <div className="auth-form-fieldset">
                <label htmlFor="learningGoals" className="auth-form-label">
                  Learning Goals
                </label>
                <textarea
                  id="learningGoals"
                  {...register('learningGoals', {
                    maxLength: {
                      value: 500,
                      message: 'Learning goals description is too long'
                    }
                  })}
                  className="auth-input"
                  rows={3}
                  placeholder="What do you hope to achieve?"
                />
                {errors.learningGoals && (
                  <p className="auth-form-error">{errors.learningGoals.message}</p>
                )}
              </div>

              <div className="auth-form-fieldset">
                <label htmlFor="preferredAiModel" className="auth-form-label">
                  Preferred AI Model
                </label>
                <select
                  id="preferredAiModel"
                  {...register('preferredAiModel')}
                  className="auth-input"
                >
                  <option value="openai">OpenAI</option>
                  <option value="gemini">Gemini</option>
                  <option value="chatkit">ChatKit</option>
                </select>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  // Progress bar component
  const ProgressBar = () => (
    <div className="multi-step-progress">
      <div className="multi-step-steps">
        <span className={`multi-step-step ${registrationStep >= 1 ? 'active' : ''}`}>Step 1</span>
        <span className={`multi-step-step ${registrationStep >= 2 ? 'active' : ''}`}>Step 2</span>
        <span className={`multi-step-step ${registrationStep >= 3 ? 'active' : ''}`}>Step 3</span>
      </div>
      <div className="multi-step-bar">
        <div
          className="multi-step-fill"
          style={{ width: `${(registrationStep / 3) * 100}%` }}
        ></div>
      </div>
    </div>
  );

  return (
    <div className="auth-form-container">
      <div className="auth-form-header">
        <h1 className="auth-form-title">Create Account</h1>
        <p className="auth-form-subtitle">Join our community to start your journey</p>
      </div>

      <ProgressBar />

      {error && (
        <div className="auth-form-error-message">
          {error}
        </div>
      )}

      <form onSubmit={(e) => {
        // Only submit the form if we're on the last step
        if (registrationStep === 3) {
          handleSubmit(onSubmit)(e);
        } else {
          e.preventDefault();
          // Just proceed to next step
          setRegistrationStep(registrationStep + 1);
        }
      }} className="space-y-6">
        {renderStep()}

        <div className="multi-step-navigation">
          {registrationStep > 1 && (
            <button
              type="button"
              onClick={() => setRegistrationStep(registrationStep - 1)}
              className="auth-button auth-button-secondary"
            >
              Back
            </button>
          )}

          <div className="multi-step-spacer"></div> {/* Spacer to push next button to the right */}

          {registrationStep < 3 ? (
            <button
              type="button"
              onClick={() => setRegistrationStep(registrationStep + 1)}
              className="auth-button auth-button-primary"
            >
              Continue
            </button>
          ) : (
            <button
              type="submit"
              disabled={isLoading}
              className={`auth-button auth-button-primary ${isLoading ? 'bg-green-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'}`}
            >
              {isLoading ? (
                <span className="flex items-center">
                  <span className="spinner"></span>
                  Creating Account...
                </span>
              ) : (
                'Complete Registration'
              )}
            </button>
          )}
        </div>
      </form>

      <div className="auth-links">
        <p>
          Already have an account?{' '}
          <a href="/auth/signin" className="auth-link">
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
};

export default UserRegistration;
