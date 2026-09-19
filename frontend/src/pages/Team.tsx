import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../api/client';
import { Button, Card, CardContent, CardHeader, CardTitle, Input } from '../components/ui';

interface UserData {
  id: string;
  email: string;
  role: string;
}

export const Team = () => {
  const { user } = useAuth();
  const [team, setTeam] = useState<UserData[]>([]);
  const [loading, setLoading] = useState(true);
  const [inviteLink, setInviteLink] = useState('');
  const [isGeneratingInvite, setIsGeneratingInvite] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const fetchTeam = async () => {
    try {
      const response = await apiClient.get('/auth/users');
      setTeam(response.data);
    } catch (error) {
      console.error("Failed to fetch team:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTeam();
  }, []);

  const handleGenerateInvite = async () => {
    setIsGeneratingInvite(true);
    try {
      const response = await apiClient.post('/auth/invite');
      const token = response.data.invite_token;
      setInviteLink(`${window.location.origin}/register?invite=${token}`);
    } catch (error) {
      console.error("Failed to generate invite:", error);
    } finally {
      setIsGeneratingInvite(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    setIsUpdating(true);
    try {
      await apiClient.patch(`/auth/users/${userId}/role`, { role: newRole });
      await fetchTeam(); // Refresh the list
    } catch (error) {
      console.error("Failed to update role:", error);
      alert("Failed to update user role. Are you sure you are an Admin?");
    } finally {
      setIsUpdating(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(inviteLink);
    alert('Invite link copied to clipboard!');
  };

  if (loading) {
    return <div className="animate-pulse flex space-x-4"><div className="flex-1 space-y-4 py-1"><div className="h-4 bg-slate-200 rounded w-3/4"></div></div></div>;
  }

  const isAdmin = user?.role === 'ADMIN';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Team Management</h1>
          <p className="text-sm text-slate-500">Manage members and roles in your organization.</p>
        </div>
        {isAdmin && (
          <Button onClick={handleGenerateInvite} disabled={isGeneratingInvite}>
            {isGeneratingInvite ? 'Generating...' : 'Generate Invite Link'}
          </Button>
        )}
      </div>

      {inviteLink && (
        <Card className="bg-blue-50 border-blue-100">
          <CardContent className="p-4 flex items-center gap-4">
            <Input readOnly value={inviteLink} className="flex-1 bg-white" />
            <Button variant="outline" onClick={copyToClipboard}>Copy</Button>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-0">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 bg-slate-50 uppercase border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-medium">Email</th>
                <th className="px-6 py-4 font-medium">Role</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {team.map((member) => (
                <tr key={member.id} className="hover:bg-slate-50/50">
                  <td className="px-6 py-4">{member.email}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                      ${member.role === 'ADMIN' ? 'bg-purple-100 text-purple-800' : ''}
                      ${member.role === 'ENGINEER' ? 'bg-blue-100 text-blue-800' : ''}
                      ${member.role === 'INSPECTOR' ? 'bg-emerald-100 text-emerald-800' : ''}
                    `}>
                      {member.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {isAdmin && member.id !== user?.id && (
                      <select 
                        className="text-sm border-slate-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        value={member.role}
                        onChange={(e) => handleRoleChange(member.id, e.target.value)}
                        disabled={isUpdating}
                      >
                        <option value="INSPECTOR">Make Inspector</option>
                        <option value="ENGINEER">Make Engineer</option>
                        <option value="ADMIN">Make Admin</option>
                      </select>
                    )}
                    {member.id === user?.id && (
                      <span className="text-slate-400 italic">You</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
};
