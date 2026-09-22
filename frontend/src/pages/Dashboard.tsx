import { useAuth } from '../hooks/useAuth';
import { AdminDashboard } from './AdminDashboard';
import { EngineerDashboard } from './EngineerDashboard';
import { InspectorDashboard } from './InspectorDashboard';

export const Dashboard = () => {
  const { user } = useAuth();
  
  if (!user) return null;
  
  if (user.role === 'ADMIN') return <AdminDashboard />;
  if (user.role === 'ENGINEER') return <EngineerDashboard />;
  return <InspectorDashboard />;
};
