import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../hooks/useAuth';
import { vi } from 'vitest';

type User = {
  id: string;
  email: string;
  role: string;
  organization_id: string;
};

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  route?: string;
  initialEntries?: string[];
  user?: User | null;
}

export function renderWithProviders(
  ui: ReactElement,
  {
    route = '/',
    initialEntries = [route],
    user = null,
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  const Wrapper = ({ children }: { children: React.ReactNode }) => {
    return (
      <AuthContext.Provider value={{ user, loading: false, loginSuccess: vi.fn(), logout: vi.fn() }}>
        <MemoryRouter initialEntries={initialEntries}>
          {children}
        </MemoryRouter>
      </AuthContext.Provider>
    );
  };

  return render(ui, { wrapper: Wrapper, ...renderOptions });
}
