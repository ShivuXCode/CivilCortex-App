import { apiClient } from './client';

export interface User {
  id: string;
  email: string;
  role: string;
  organization_id: string;
}

export const login = async (email: string, password: string) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await apiClient.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const register = async (email: string, password: string, inviteToken?: string) => {
  const response = await apiClient.post('/auth/register', {
    email,
    password,
    invite_token: inviteToken || undefined
  });
  return response.data;
};

export const generateInvite = async () => {
  const response = await apiClient.post('/auth/invite');
  return response.data;
};

export const getMe = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};
