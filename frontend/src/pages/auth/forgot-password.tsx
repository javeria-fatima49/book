import React, { useState } from 'react';

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real implementation, this would call auth API to send reset link
    console.log('Reset password requested for:', email);
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow mt-12">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Check your email</h2>
          <p>We've sent a password reset link to {email}.</p>
          <p className="mt-4">
            Didn't receive it? <a href="#" className="text-blue-500 hover:underline">Resend email</a>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow mt-12">
      <h1 className="text-3xl font-bold mb-6 text-center">Reset Password</h1>
      <p className="mb-6 text-center">Enter your email address and we'll send you a link to reset your password.</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="your@email.com"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Send Reset Link
        </button>
      </form>

      <div className="mt-4 text-center">
        <p>
          Remember your password?{' '}
          <a href="/auth/signin" className="text-blue-500 hover:underline">Sign in</a>
        </p>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;