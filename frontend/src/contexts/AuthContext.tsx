import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { simpleAuthAPI, User } from '../lib/simple-auth-api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  authenticated: boolean;
  signIn: (email: string, password: string) => Promise<{ error?: string }>;
  signUp: (email: string, password: string, firstName: string, lastName: string, userData?: Partial<User>) => Promise<{ error?: string }>;
  signOut: () => void;
  fetchUser: () => Promise<User | null>;
}

const defaultAuthContext: AuthContextType = {
  user: null,
  loading: true,
  authenticated: false,
  signIn: async () => ({ error: 'Auth not initialized' }),
  signUp: async () => ({ error: 'Auth not initialized' }),
  signOut: () => {},
  fetchUser: async () => null,
};

const AuthContext = createContext<AuthContextType>(defaultAuthContext);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const initAuth = async () => {
      try {
        setLoading(true);
        const session = await simpleAuthAPI.getSession();

        if (isMounted && session.user) {
          setUser(session.user);
          setAuthenticated(true);
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    initAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  const signIn = async (email: string, password: string): Promise<{ error?: string }> => {
    try {
      setLoading(true);
      setAuthenticated(false);
      const result = await simpleAuthAPI.signIn(email, password);

      if (result.error) {
        return { error: result.error };
      }

      if (result.user) {
        setUser(result.user);
        setAuthenticated(true);
      }

      return {};
    } catch (error: any) {
      return { error: error.message || 'Login failed' };
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (
    email: string,
    password: string,
    firstName: string,
    lastName: string,
    userData?: Partial<User>
  ): Promise<{ error?: string }> => {
    try {
      setLoading(true);
      setAuthenticated(false);
      const result = await simpleAuthAPI.signUp(email, password, firstName, lastName, userData);

      if (result.error) {
        return { error: result.error };
      }

      if (result.user) {
        setUser(result.user);
        setAuthenticated(true);
      }

      return {};
    } catch (error: any) {
      return { error: error.message || 'Registration failed' };
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    try {
      await simpleAuthAPI.signOut();
      setUser(null);
      setAuthenticated(false);
    } catch (error) {
      console.error('Sign out error:', error);
    }
  };

  const fetchUser = async (): Promise<User | null> => {
    try {
      const session = await simpleAuthAPI.getSession();
      if (session.user) {
        setUser(session.user);
        return session.user;
      }
      return null;
    } catch (error) {
      console.error('Error fetching user:', error);
      return null;
    }
  };

  const value = {
    user,
    loading,
    authenticated,
    signIn,
    signUp,
    signOut,
    fetchUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
};