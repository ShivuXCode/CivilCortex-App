import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, Button } from '../components/ui';
import { getBuildings, getBuilding, Building, BuildingDetail } from '../api/hierarchy';
import { createInspection, uploadInspectionImage, analyzeImage } from '../api/inspections';
import { getAnalysisJob, AnalysisJobResponse } from '../api/analysis';
import { UploadCloud, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';

export const NewInspection = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [buildingDetail, setBuildingDetail] = useState<BuildingDetail | null>(null);
  
  // Selection State
  const [selectedBuildingId, setSelectedBuildingId] = useState('');
  const [selectedFloorId, setSelectedFloorId] = useState('');
  const [selectedAreaId, setSelectedAreaId] = useState('');
  const [selectedElementId, setSelectedElementId] = useState('');

  // Workflow State
  const [inspectionId, setInspectionId] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  
  // Job State
  const [jobId, setJobId] = useState('');
  const [jobStatus, setJobStatus] = useState<AnalysisJobResponse['status'] | ''>('');
  const [jobError, setJobError] = useState<string | null>(null);

  useEffect(() => {
    getBuildings().then(setBuildings).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedBuildingId) {
      getBuilding(selectedBuildingId).then(setBuildingDetail).catch(console.error);
    }
  }, [selectedBuildingId]);

  // Polling Effect with 90-second timeout to prevent infinite loading states
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    let timeoutHandle: ReturnType<typeof setTimeout>;

    const pollJob = async () => {
      if (!jobId || jobStatus === 'COMPLETED' || jobStatus === 'FAILED') return;
      try {
        const res = await getAnalysisJob(jobId);
        setJobStatus(res.status);
        if (res.error_message) {
          setJobError(res.error_message);
        }
      } catch (err) {
        console.error("Failed to fetch job status", err);
      }
    };

    if (jobId && jobStatus !== 'COMPLETED' && jobStatus !== 'FAILED') {
      interval = setInterval(pollJob, 2000);
      // Safety timeout: after 90 seconds stop polling and show a stuck-job message
      timeoutHandle = setTimeout(() => {
        clearInterval(interval);
        if (jobStatus !== 'COMPLETED' && jobStatus !== 'FAILED') {
          setJobStatus('FAILED');
          setJobError('Analysis is taking too long. The job may be stuck. Please try again or contact support.');
        }
      }, 90000);
    }

    return () => {
      if (interval) clearInterval(interval);
      if (timeoutHandle) clearTimeout(timeoutHandle);
    };
  }, [jobId, jobStatus]);

  const handleStartInspection = async () => {
    if (!selectedBuildingId || !selectedElementId) return;
    try {
      // Pass structural_element_id so the backend links the image/analysis
      // to the specific element selected in Step 1 (fixes the element context gap)
      const insp = await createInspection({
        building_id: selectedBuildingId,
        structural_element_id: selectedElementId,
      });
      setInspectionId(insp.id);
      setStep(2);
    } catch (err: any) {
      console.error("Failed to start inspection", err);
      alert("Failed to start inspection. Please check your connection or try again.");
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0]);
    }
  };

  const submitImageForAnalysis = async () => {
    if (!imageFile || !inspectionId) return;
    setIsUploading(true);
    try {
      // 1. Upload
      const imgRes = await uploadInspectionImage(inspectionId, imageFile);
      
      // 2. Analyze
      const result = await analyzeImage(inspectionId, imgRes.id);
      setJobId(result.job_id);
      setJobStatus(result.status as AnalysisJobResponse['status']);
      setStep(3);
    } catch (err) {
      console.error("Failed to upload or trigger analysis");
      alert("Failed to upload image or trigger analysis. Please check supported formats and backend connectivity.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">New Inspection</h1>
        <p className="text-slate-500 dark:text-slate-400">Record a new structural observation in the field.</p>
      </div>

      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>1. Select Structural Location</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label htmlFor="building-select" className="text-sm font-medium text-slate-700 dark:text-slate-300">Building</label>
              <select 
                id="building-select"
                className="mt-1 block w-full rounded-md border-slate-300 dark:border-slate-600 py-2 pl-3 pr-10 text-base focus:border-slate-500 focus:outline-none focus:ring-slate-500 sm:text-sm border bg-white dark:bg-slate-800"
                value={selectedBuildingId}
                onChange={(e) => {
                  setSelectedBuildingId(e.target.value);
                  setSelectedFloorId(''); setSelectedAreaId(''); setSelectedElementId('');
                }}
              >
                <option value="">-- Select Building --</option>
                {buildings.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>

            {buildingDetail && (
              <div>
                <label htmlFor="floor-select" className="text-sm font-medium text-slate-700 dark:text-slate-300">Floor</label>
                <select 
                  id="floor-select"
                  className="mt-1 block w-full rounded-md border-slate-300 dark:border-slate-600 py-2 pl-3 pr-10 text-base focus:border-slate-500 focus:outline-none focus:ring-slate-500 sm:text-sm border bg-white dark:bg-slate-800"
                  value={selectedFloorId}
                  onChange={(e) => {
                    setSelectedFloorId(e.target.value);
                    setSelectedAreaId(''); setSelectedElementId('');
                  }}
                >
                  <option value="">-- Select Floor --</option>
                  {buildingDetail.floors.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
                </select>
                {/* Real app would allow creating missing hierarchy here, skipping for brevity of shell unless explicitly needed */}
              </div>
            )}

            {selectedFloorId && buildingDetail && (
              <div>
                <label htmlFor="area-select" className="text-sm font-medium text-slate-700 dark:text-slate-300">Area</label>
                <select 
                  id="area-select"
                  className="mt-1 block w-full rounded-md border-slate-300 dark:border-slate-600 py-2 pl-3 pr-10 text-base focus:border-slate-500 focus:outline-none focus:ring-slate-500 sm:text-sm border bg-white dark:bg-slate-800"
                  value={selectedAreaId}
                  onChange={(e) => {
                    setSelectedAreaId(e.target.value);
                    setSelectedElementId('');
                  }}
                >
                  <option value="">-- Select Area --</option>
                  {buildingDetail.floors.find(f => f.id === selectedFloorId)?.areas.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
                </select>
              </div>
            )}

            {selectedAreaId && buildingDetail && (
              <div>
                <label htmlFor="element-select" className="text-sm font-medium text-slate-700 dark:text-slate-300">Structural Element</label>
                <select 
                  id="element-select"
                  className="mt-1 block w-full rounded-md border-slate-300 dark:border-slate-600 py-2 pl-3 pr-10 text-base focus:border-slate-500 focus:outline-none focus:ring-slate-500 sm:text-sm border bg-white dark:bg-slate-800"
                  value={selectedElementId}
                  onChange={(e) => setSelectedElementId(e.target.value)}
                >
                  <option value="">-- Select Element --</option>
                  {buildingDetail.floors.find(f => f.id === selectedFloorId)?.areas.find(a => a.id === selectedAreaId)?.structural_elements.map(e => <option key={e.id} value={e.id}>{e.name} ({e.element_type})</option>)}
                </select>
              </div>
            )}

            <div className="pt-4 flex justify-end">
              <Button disabled={!selectedElementId} onClick={handleStartInspection}>
                Continue to Image Inspection
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>2. Capture Defect</CardTitle>
            <p className="text-sm text-slate-500 dark:text-slate-400">Capture the defect as clearly as possible. Include a scale/reference when physical measurements are required.</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-12 text-center hover:bg-slate-50 dark:bg-slate-900/50 transition-colors">
              <UploadCloud className="mx-auto h-12 w-12 text-slate-400 mb-4" />
              <div className="flex text-sm text-slate-600 dark:text-slate-400 justify-center">
                <label htmlFor="file-upload" className="relative cursor-pointer rounded-md font-medium text-slate-900 dark:text-white focus-within:outline-none focus-within:ring-2 focus-within:ring-slate-500 focus-within:ring-offset-2 hover:text-slate-700 dark:text-slate-300">
                  <span>Upload a file</span>
                  <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/jpeg,image/png,image/webp" onChange={handleImageUpload} />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">PNG, JPG, WEBP up to 20MB</p>
            </div>
            
            {imageFile && (
              <div className="flex items-center gap-4 bg-slate-50 dark:bg-slate-900/50 p-4 rounded-md border border-slate-200 dark:border-slate-700">
                <div className="h-16 w-16 bg-slate-200 rounded object-cover overflow-hidden flex-shrink-0">
                  <img src={URL.createObjectURL(imageFile)} alt="Preview" className="h-full w-full object-cover" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 dark:text-white truncate">{imageFile.name}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{(imageFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
            )}

            <div className="pt-4 flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setStep(1)} disabled={isUploading}>Back</Button>
              <Button onClick={submitImageForAnalysis} disabled={!imageFile || isUploading}>
                {isUploading ? 'Validating & Analyzing...' : 'Analyze Image'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 3 && (
        <Card className="border-slate-200 dark:border-slate-700">
          <CardHeader className={jobStatus === 'COMPLETED' ? "bg-slate-900 text-white rounded-t-xl" : "bg-slate-100 dark:bg-slate-900 rounded-t-xl border-b border-slate-200 dark:border-slate-700"}>
            <CardTitle className="flex items-center gap-2">
              {jobStatus === 'COMPLETED' ? (
                <CheckCircle className="h-5 w-5 text-emerald-400" />
              ) : jobStatus === 'FAILED' ? (
                <AlertTriangle className="h-5 w-5 text-red-500" />
              ) : (
                <Loader2 className="h-5 w-5 animate-spin text-slate-500 dark:text-slate-400" />
              )}
              {jobStatus === 'QUEUED' && "Analysis Queued..."}
              {jobStatus === 'PROCESSING' && "Analysis In Progress..."}
              {jobStatus === 'COMPLETED' && "Analysis Completed"}
              {jobStatus === 'FAILED' && "Analysis Failed"}
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6 space-y-6">
            
            {(jobStatus === 'QUEUED' || jobStatus === 'PROCESSING') && (
              <div className="text-center py-12 space-y-4">
                <p className="text-slate-600 dark:text-slate-400">Please wait while our models and AI agents evaluate the structural defect.</p>
                <p className="text-sm text-slate-400">This may take up to 60 seconds.</p>
              </div>
            )}

            {jobStatus === 'COMPLETED' && (
              <div className="space-y-6 text-center py-6">
                <p className="text-slate-700 dark:text-slate-300 font-medium text-lg">Defect observation captured and analysis generated successfully.</p>
                <div className="pt-4 flex justify-center">
                  <Button onClick={() => navigate(`/inspections/${inspectionId}/report`)}>
                    View Engineering Report
                  </Button>
                </div>
              </div>
            )}

            {jobStatus === 'FAILED' && (
              <div className="space-y-4">
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <p className="text-sm font-medium text-red-800">Error during analysis processing</p>
                  <p className="text-sm text-red-700 mt-1">{jobError || "An unknown error occurred."}</p>
                </div>
                <div className="pt-4 flex justify-end">
                  <Button variant="ghost" onClick={() => {
                    setJobId('');
                    setJobStatus('');
                    setStep(2);
                  }}>
                    Try Again
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};
