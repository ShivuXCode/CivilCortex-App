import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../components/ui';
import { getInspections, Inspection, assignEngineer } from '../api/inspections';
import { apiClient } from '../api/client';
import { User } from '../api/auth';

export const AdminDashboard = () => {
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [engineers, setEngineers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [inspectionsRes, usersRes] = await Promise.all([
          getInspections(),
          apiClient.get('/auth/users')
        ]);
        setInspections(inspectionsRes);
        setEngineers(usersRes.data.filter((u: User) => u.role === 'ENGINEER'));
      } catch (err) {
        console.error("Failed to load admin data");
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleAssign = async (inspectionId: string, engineerId: string) => {
    try {
      await assignEngineer(inspectionId, engineerId);
      // Refresh
      const updated = await getInspections();
      setInspections(updated);
    } catch (err) {
      alert("Failed to assign engineer");
    }
  };

  if (isLoading) return <div className="p-8">Loading admin dashboard...</div>;

  const submittedInspections = inspections.filter(i => i.status === 'SUBMITTED' && !i.assigned_engineer_id);
  const activeInspections = inspections.filter(i => i.status !== 'COMPLETED' && i.status !== 'DRAFT');

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Admin Dashboard</h1>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Needs Assignment</CardTitle>
          </CardHeader>
          <CardContent>
            {submittedInspections.length === 0 ? (
              <p className="text-slate-500">No inspections waiting for assignment.</p>
            ) : (
              <div className="space-y-4">
                {submittedInspections.map(insp => (
                  <div key={insp.id} className="p-4 border rounded flex flex-col gap-2">
                    <div className="font-medium">Inspection {insp.id.substring(0,8)}</div>
                    <div className="flex gap-2">
                      <select 
                        className="flex-1 border rounded p-1"
                        id={`engineer-select-${insp.id}`}
                      >
                        <option value="">Select Engineer</option>
                        {engineers.map(e => (
                          <option key={e.id} value={e.id}>{e.full_name || e.email}</option>
                        ))}
                      </select>
                      <Button onClick={() => {
                        const select = document.getElementById(`engineer-select-${insp.id}`) as HTMLSelectElement;
                        if (select.value) handleAssign(insp.id, select.value);
                      }}>Assign</Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Inspections</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {activeInspections.map(insp => (
                <div key={insp.id} className="flex justify-between items-center p-2 border-b">
                  <span>{insp.id.substring(0,8)}</span>
                  <span className="text-xs px-2 py-1 bg-slate-100 rounded-full">{insp.status}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
