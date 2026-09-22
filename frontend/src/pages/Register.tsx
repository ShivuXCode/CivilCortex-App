import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { register as registerApi, login } from '../api/auth';
import { Button, Input, Card, CardContent, CardHeader, CardTitle } from '../components/ui';

export const Register = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [role, setRole] = useState('INSPECTOR');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { loginSuccess } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get('invite');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setIsLoading(true);

    try {
      // 1. Register the user
      await registerApi(email, password, fullName, organizationName, role, inviteToken || undefined);
      // 2. Automatically log them in
      const data = await login(email, password);
      loginSuccess(data.access_token, data.refresh_token);
      navigate('/');
    } catch (err: any) {
      if (err.civilCortexMessage) {
        setError(err.civilCortexMessage);
      } else if (typeof err.response?.data?.detail === 'string') {
        setError(err.response.data.detail);
      } else {
        setError('Unable to register. Please check your inputs and try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center pb-8 pt-8">
          <CardTitle className="text-3xl font-bold tracking-tight text-slate-900">CivilCortex</CardTitle>
          <p className="text-sm text-slate-500 mt-2">
            {inviteToken ? 'Join your organization' : 'Create a new organization account'}
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 text-red-700 p-3 rounded-md text-sm border border-red-200">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none text-slate-700" htmlFor="fullName">
                Full Name
              </label>
              <Input
                id="fullName"
                type="text"
                placeholder="Jane Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none text-slate-700" htmlFor="email">
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="engineer@civilcortex.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none text-slate-700" htmlFor="password">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
                minLength={8}
              />
              <p className="text-xs text-slate-500">Must be at least 8 characters</p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none text-slate-700" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={isLoading}
                minLength={8}
              />
            </div>
            {!inviteToken && (
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none text-slate-700" htmlFor="organizationName">
                  Organization / Company Name
                </label>
                <Input
                  id="organizationName"
                  type="text"
                  placeholder="Acme Engineering Ltd."
                  value={organizationName}
                  onChange={(e) => setOrganizationName(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none text-slate-700" htmlFor="role">
                Role
              </label>
              <select
                id="role"
                className="flex h-10 w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                disabled={isLoading}
              >
                <option value="INSPECTOR">Inspector (Field App)</option>
                <option value="ENGINEER">Engineer (Reviewer)</option>
                {!inviteToken && <option value="ADMIN">Administrator</option>}
              </select>
            </div>
            <Button type="submit" className="w-full mt-6" disabled={isLoading}>
              {isLoading ? 'Creating account...' : 'Create Account'}
            </Button>
            
            <div className="text-center mt-4 pt-4 border-t border-slate-100">
              <p className="text-sm text-slate-500">
                Already have an account?{' '}
                <Link to="/login" className="text-blue-600 hover:underline">
                  Sign in
                </Link>
              </p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
