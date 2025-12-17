/**
 * Better Auth SDK - Example Usage
 * 
 * This file demonstrates how to use the signup and signin functions
 * with proper async/await and error handling.
 */

// Example Signup Usage
async function exampleSignup() {
  try {
    // Get auth context from your React app
    const { signUp } = useAuth(); // This would be within a React component

    // Example signup with basic user data
    const result = await signUp(
      'user@example.com',      // email
      'SecurePassword123!',    // password
      'John',                  // firstName
      'Doe',                   // lastName
      {                        // Additional user data (optional)
        developerLevel: 'intermediate',
        programmingLanguages: 'JavaScript,Python',
        yearsExperience: 5,
        roboticsInterests: 'Autonomous navigation',
        learningGoals: 'Master AI for robotics',
        preferredAiModel: 'openai'
      }
    );

    if (result.error) {
      console.error('Signup failed:', result.error);
      // Handle specific error cases
      if (result.error.includes('already exists')) {
        console.log('User already exists, redirecting to login...');
        // Redirect to login page
      } else {
        console.log('Signup error occurred, please try again.');
      }
    } else {
      console.log('User successfully registered!');
      // Redirect to dashboard or onboarding
      window.location.href = '/dashboard';
    }
  } catch (error) {
    console.error('Unexpected error during signup:', error);
    // Handle network errors, server errors, etc.
  }
}

// Example Signin Usage
async function exampleSignin() {
  try {
    // Get auth context from your React app
    const { signIn } = useAuth(); // This would be within a React component

    // Example sign in
    const result = await signIn(
      'user@example.com',      // email
      'SecurePassword123!'     // password
    );

    if (result.error) {
      console.error('Signin failed:', result.error);
      // Handle specific error cases
      if (result.error.includes('invalid credentials')) {
        console.log('Invalid email or password, please try again.');
      } else {
        console.log('Signin error occurred, please try again.');
      }
    } else {
      console.log('User successfully signed in!');
      // Redirect to dashboard
      window.location.href = '/dashboard';
    }
  } catch (error) {
    console.error('Unexpected error during signin:', error);
    // Handle network errors, server errors, etc.
  }
}

// Example form handler for signup
async function handleSignupForm(formData) {
  try {
    const { signUp } = useAuth();
    
    const result = await signUp(
      formData.email,
      formData.password,
      formData.firstName,
      formData.lastName,
      {
        developerLevel: formData.developerLevel,
        roboticsInterests: formData.roboticsInterests,
        programmingLanguages: formData.programmingLanguages,
        yearsExperience: parseInt(formData.yearsExperience),
        learningGoals: formData.learningGoals,
        preferredAiModel: formData.preferredAiModel
      }
    );

    if (result.error) {
      // Show error to user
      displayError(result.error);
    } else {
      // Success - redirect or show success message
      displaySuccess('Registration successful! Redirecting...');
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 2000);
    }
  } catch (error) {
    console.error('Signup error:', error);
    displayError('An unexpected error occurred. Please try again.');
  }
}

// Example form handler for signin
async function handleSigninForm(formData) {
  try {
    const { signIn } = useAuth();
    
    const result = await signIn(
      formData.email,
      formData.password
    );

    if (result.error) {
      // Show error to user
      displayError(result.error);
    } else {
      // Success - redirect or show success message
      displaySuccess('Login successful! Redirecting...');
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 2000);
    }
  } catch (error) {
    console.error('Signin error:', error);
    displayError('An unexpected error occurred. Please try again.');
  }
}

// Helper functions for UI feedback
function displayError(message) {
  // Example: Show error in UI
  const errorElement = document.getElementById('auth-error');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  }
  console.error('Auth error:', message);
}

function displaySuccess(message) {
  // Example: Show success in UI
  const successElement = document.getElementById('auth-success');
  if (successElement) {
    successElement.textContent = message;
    successElement.style.display = 'block';
  }
  console.log('Auth success:', message);
}

// Usage within a React component
function AuthComponent() {
  const { signIn, signUp, loading, user } = useAuth();

  // Sign up handler
  const handleSignUp = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const result = await signUp(
      formData.get('email'),
      formData.get('password'),
      formData.get('firstName'),
      formData.get('lastName')
    );

    if (result.error) {
      // Handle error
      alert(result.error);
    } else {
      // Handle success
      alert('Registration successful!');
    }
  };

  // Sign in handler
  const handleSignIn = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const result = await signIn(
      formData.get('email'),
      formData.get('password')
    );

    if (result.error) {
      // Handle error
      alert(result.error);
    } else {
      // Handle success
      alert('Login successful!');
    }
  };

  return (
    <div>
      {user ? (
        <p>Welcome, {user.firstName}!</p>
      ) : (
        <div>
          <form onSubmit={handleSignIn}>
            <input name="email" type="email" placeholder="Email" required />
            <input name="password" type="password" placeholder="Password" required />
            <button type="submit">Sign In</button>
          </form>
        </div>
      )}
    </div>
  );
}

// Error handling for common cases
function handleAuthError(error, type = 'general') {
  let userMessage = 'An error occurred. Please try again.';
  
  // Handle specific error cases based on message content
  if (error.includes('already exists')) {
    userMessage = 'A user with this email already exists. Try logging in instead.';
  } else if (error.includes('invalid credentials') || error.includes('password')) {
    userMessage = 'Invalid email or password. Please check your credentials.';
  } else if (error.includes('network') || error.includes('fetch')) {
    userMessage = 'Network error. Please check your connection and try again.';
  } else if (error.includes('timeout')) {
    userMessage = 'Request timed out. Please try again.';
  }
  
  console.error(`Auth ${type} error:`, error);
  return userMessage;
}

export { 
  exampleSignup, 
  exampleSignin, 
  handleSignupForm, 
  handleSigninForm, 
  handleAuthError,
  displayError,
  displaySuccess
};