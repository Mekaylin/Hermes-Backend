import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { firebaseAuth } from '../config/firebase';
import config from '../config';

interface User {
  uid: string;
  email: string | null;
  displayName?: string | null;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = firebaseAuth.onAuthStateChanged((firebaseUser: any) => {
      if (firebaseUser) {
        setUser({
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          displayName: firebaseUser.displayName,
        });
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    try {
      setLoading(true);
      
      if (config.mockMode) {
        // Mock login for development
        await new Promise(resolve => setTimeout(resolve, 1000));
        setUser({ uid: 'mock-user', email });
        localStorage.setItem('authToken', 'mock-token');
        return;
      }
      
      const result = await firebaseAuth.signInWithEmailAndPassword(email, password);
      const token = await result.user.getIdToken();
      localStorage.setItem('authToken', token);
    } catch (error: any) {
      throw new Error(error.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, password: string): Promise<void> => {
    try {
      setLoading(true);
      
      if (config.mockMode) {
        // Mock registration for development
        await new Promise(resolve => setTimeout(resolve, 1000));
        setUser({ uid: 'mock-user', email });
        localStorage.setItem('authToken', 'mock-token');
        return;
      }
      
      const result = await firebaseAuth.createUserWithEmailAndPassword(email, password);
      const token = await result.user.getIdToken();
      localStorage.setItem('authToken', token);
    } catch (error: any) {
      throw new Error(error.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      setLoading(true);
      
      if (config.mockMode) {
        // Mock logout
        await new Promise(resolve => setTimeout(resolve, 500));
        setUser(null);
        localStorage.removeItem('authToken');
        return;
      }
      
      await firebaseAuth.signOut();
      localStorage.removeItem('authToken');
    } catch (error: any) {
      throw new Error(error.message || 'Logout failed');
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (email: string): Promise<void> => {
    try {
      if (config.mockMode) {
        // Mock password reset
        await new Promise(resolve => setTimeout(resolve, 1000));
        return;
      }
      
      await firebaseAuth.sendPasswordResetEmail(email);
    } catch (error: any) {
      throw new Error(error.message || 'Password reset failed');
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    resetPassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
