import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { Card, CardContent, CardHeader, CardTitle, Button } from './ui';
import { X, Clock, AlertTriangle } from 'lucide-react';

interface AuditLog {
  id: string;
  user_id: string;
  action: string;
  previous_state: any;
  new_state: any;
  created_at: string;
}

interface AuditHistoryModalProps {
  assessmentId: string;
  onClose: () => void;
}

export const AuditHistoryModal: React.FC<AuditHistoryModalProps> = ({ assessmentId, onClose }) => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await apiClient.get(`/defects/assessments/${assessmentId}/audit-logs`);
        setLogs(response.data);
      } catch (error) {
        console.error("Failed to fetch audit logs", error);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, [assessmentId]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] flex flex-col bg-white dark:bg-slate-800">
        <CardHeader className="flex flex-row items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-slate-500 dark:text-slate-400" />
            <CardTitle className="text-xl">Audit History</CardTitle>
          </div>
          <Button variant="outline" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="animate-pulse space-y-4">
              <div className="h-20 bg-slate-100 dark:bg-slate-900 rounded-md"></div>
              <div className="h-20 bg-slate-100 dark:bg-slate-900 rounded-md"></div>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center text-slate-500 dark:text-slate-400 py-8">
              No historical changes found for this assessment.
            </div>
          ) : (
            <div className="space-y-6">
              {logs.map((log) => (
                <div key={log.id} className="relative pl-6 border-l-2 border-slate-200 dark:border-slate-700">
                  <div className="absolute -left-1.5 mt-1.5 w-3 h-3 bg-blue-500 rounded-full ring-4 ring-white" />
                  <div className="bg-slate-50 dark:bg-slate-900/50 rounded-lg p-4 text-sm">
                    <div className="flex justify-between text-slate-500 dark:text-slate-400 mb-2">
                      <span className="font-medium text-slate-700 dark:text-slate-300">User: {log.user_id}</span>
                      <span>{new Date(log.created_at).toLocaleString()}</span>
                    </div>
                    
                    {log.action === "UPDATE" && (
                      <div className="space-y-2 mt-4">
                        {Object.keys(log.new_state).map(key => {
                          const oldVal = log.previous_state?.[key];
                          const newVal = log.new_state?.[key];
                          if (oldVal !== newVal && key !== "updated_at") {
                            return (
                              <div key={key} className="grid grid-cols-[100px_1fr_auto_1fr] gap-2 items-center">
                                <span className="font-medium text-slate-600 dark:text-slate-400 capitalize">{key.replace('_', ' ')}</span>
                                <span className="bg-red-50 text-red-700 px-2 py-1 rounded strike-through line-through truncate">{oldVal || 'None'}</span>
                                <span className="text-slate-400">→</span>
                                <span className="bg-green-50 text-green-700 px-2 py-1 rounded font-medium truncate">{newVal || 'None'}</span>
                              </div>
                            );
                          }
                          return null;
                        })}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded-lg flex items-start gap-3 mt-8">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium">Liability Notice</p>
                  <p className="text-yellow-700 mt-1">This audit trail is permanently stored in the database to track manual overrides of AI-generated assessments.</p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
