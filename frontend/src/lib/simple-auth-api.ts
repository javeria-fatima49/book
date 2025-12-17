// Simple API client for Better Auth
interface User {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  developerLevel?: string;
  roboticsInterests?: string;
  preferredAiModel?: string;
  learningGoals?: string;
  programmingLanguages?: string;
  yearsExperience?: number;
}

interface AuthResponse {
  user?: User;
  session?: any;
  error?: string;
}

const AUTH_BASE_URL = "http://localhost:3003/api/auth";

export const simpleAuthAPI = {
  async signUp(
    email: string,
    password: string,
    firstName: string,
    lastName: string,
    userData?: Partial<User>
  ): Promise<AuthResponse> {
    try {
      const response = await fetch(`${AUTH_BASE_URL}/sign-up`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email,
          password,
          firstName,
          lastName,
          ...userData
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        return { error: data.message || 'Registration failed' };
      }

      return { ...data };
    } catch (error) {
      return { error: 'Network error' };
    }
  },

  async signIn(email: string, password: string): Promise<AuthResponse> {
    try {
      const response = await fetch(`${AUTH_BASE_URL}/sign-in`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        return { error: data.message || 'Login failed' };
      }

      return { ...data };
    } catch (error) {
      return { error: 'Network error' };
    }
  },

  async signOut(): Promise<AuthResponse> {
    try {
      const response = await fetch(`${AUTH_BASE_URL}/sign-out`, {
        method: 'POST',
        credentials: 'include',
      });

      const data = await response.json();
      
      if (!response.ok) {
        return { error: data.message || 'Sign out failed' };
      }

      return { ...data };
    } catch (error) {
      return { error: 'Network error' };
    }
  },

  async getSession(): Promise<AuthResponse> {
    try {
      const response = await fetch(`${AUTH_BASE_URL}/session`, {
        method: 'GET',
        credentials: 'include',
      });

      const data = await response.json();
      
      if (!response.ok) {
        return { error: data.message || 'Could not get session' };
      }

      return { ...data };
    } catch (error) {
      return { error: 'Network error' };
    }
  },
};

export type { User, AuthResponse };