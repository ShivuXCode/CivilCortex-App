import React, { createContext, useContext, useState, useEffect } from 'react';
import { getMe, User } from '../api/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  loginSuccess: (accessToken: string, refreshToken?: string) => void;
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

  const loginSuccess = (accessToken: string, refreshToken?: string) => {
    localStorage.setItem('civilcortex_token', accessToken);
    if (refreshToken) {
      localStorage.setItem('civilcortex_refresh_token', refreshToken);
    }
    setLoading(true);
    fetchUser();
  };

  const logout = () => {
    localStorage.removeItem('civilcortex_token');
    localStorage.removeItem('civilcortex_refresh_token');
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
