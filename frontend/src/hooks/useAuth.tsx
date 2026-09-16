import React, { createContext, useContext, useState, useEffect } from 'react';
import { getMe, User } from '../api/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  loginSuccess: (token: string) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  loginSuccess: () => {},
  logout: () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = async () => {
    try {
      const data = await getMe();
      setUser(data);
    } catch (err) {
      setUser(null);
      localStorage.removeItem('civilcortex_token');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('civilcortex_token');
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const loginSuccess = (token: string) => {
    localStorage.setItem('civilcortex_token', token);
    setLoading(true);
    fetchUser();
  };

  const logout = () => {
    localStorage.removeItem('civilcortex_token');
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginSuccess, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
