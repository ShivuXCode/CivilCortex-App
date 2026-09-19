import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../components/ui';
import { getBuildings } from '../api/hierarchy';
import { getInspections } from '../api/inspections';
import { getDefects } from '../api/defects';

export const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    buildings: 0,
    activeInspections: 0,
    openDefects: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [buildings, inspections, defects] = await Promise.all([
          getBuildings(),
          getInspections(),
          getDefects()
        ]);
        
        // Open defects are those that need attention (not repaired or dismissed)
        const openDefectsCount = defects.filter(d => 
          d.status === 'CANDIDATE' || d.status === 'MONITORED'
        ).length;
        
        setStats({
          buildings: buildings.length,
          activeInspections: inspections.length,
          openDefects: openDefectsCount
        });
      } catch (err) {
        console.error("Failed to load dashboard data");
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return <div className="p-8 text-slate-500">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Dashboard</h1>
        <p className="text-slate-500">Overview of your inspection portfolio.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Buildings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.buildings}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Inspections</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeInspections}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Defects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{stats.openDefects}</div>
            <p className="text-xs text-slate-500 mt-1">Requires attention</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <Button onClick={() => navigate('/inspections/new')} className="justify-start">
              Start New Inspection
            </Button>
            <Button variant="secondary" onClick={() => navigate('/buildings')} className="justify-start">
              View Buildings
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
