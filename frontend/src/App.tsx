import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Buildings } from './pages/Buildings';
import { BuildingDetail } from './pages/BuildingDetail';
import { NewInspection } from './pages/NewInspection';
import { Defects } from './pages/Defects';
import { Report } from './pages/Report';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="h-screen flex items-center justify-center bg-slate-100 text-slate-500">Loading CivilCortex...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

const Placeholder = ({ title }: { title: string }) => (
  <div className="space-y-6">
    <div>
      <h1 className="text-2xl font-bold tracking-tight text-slate-900">{title}</h1>
      <p className="text-slate-500">This module is scheduled for a future development phase.</p>
    </div>
  </div>
);

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route path="/" element={<PrivateRoute><DashboardLayout /></PrivateRoute>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        
        <Route path="buildings">
          <Route index element={<Buildings />} />
          <Route path=":id" element={<BuildingDetail />} />
        </Route>

        <Route path="inspections">
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="new" element={<NewInspection />} />
          <Route path=":id/report" element={<Report />} />
        </Route>

        <Route path="defects" element={<Defects />} />
        <Route path="monitoring" element={<Placeholder title="Monitoring" />} />
        <Route path="reports" element={<Placeholder title="Reports" />} />
        
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
