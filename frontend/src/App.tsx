import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Inspections } from './pages/Inspections';
import { Reports } from './pages/Reports';
import { Buildings } from './pages/Buildings';
import { BuildingDetail } from './pages/BuildingDetail';
import { NewInspection } from './pages/NewInspection';
import { Defects } from './pages/Defects';
import { DefectDetail } from './pages/DefectDetail';
import { Report } from './pages/Report';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="h-screen flex items-center justify-center bg-slate-100 dark:bg-slate-900 text-slate-500 dark:text-slate-400">Loading CivilCortex...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

const Placeholder = ({ title }: { title: string }) => (
  <div className="space-y-6">
    <div>
      <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">{title}</h1>
      <p className="text-slate-500 dark:text-slate-400">This module is scheduled for a future development phase.</p>
    </div>
  </div>
);

import { Register } from './pages/Register';
import { Team } from './pages/Team';
import { Settings } from './pages/Settings';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';

function AppRoutes() {
  useTheme();
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<PrivateRoute><DashboardLayout /></PrivateRoute>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        
        <Route path="buildings">
          <Route index element={<Buildings />} />
          <Route path=":id" element={<BuildingDetail />} />
        </Route>

        <Route path="inspections">
          <Route index element={<Inspections />} />
          <Route path="new" element={<NewInspection />} />
          <Route path=":id/report" element={<Report />} />
        </Route>

        <Route path="defects">
          <Route index element={<Defects />} />
          <Route path=":id" element={<DefectDetail />} />
        </Route>
        <Route path="team" element={<Team />} />
        <Route path="reports" element={<Reports />} />
        <Route path="settings" element={<Settings />} />
        
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
