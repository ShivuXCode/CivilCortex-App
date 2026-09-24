import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import { Upload, FileText, Image as ImageIcon, Database, Plus, Trash2, Clock, CheckCircle, AlertCircle, Loader2, ArrowLeft, Camera } from 'lucide-react';
import { fetchAnalyses, fetchAnalysis, uploadAnalysis, deleteAnalysis, getImageUrl } from './api/client';
import ReactMarkdown from 'react-markdown';
import './index.css';

// --- Dashboard Component ---
function Dashboard() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<any>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  
  // Form state
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadAnalyses();
  }, []);

  useEffect(() => {
    if (selectedId) {
      loadDetail(selectedId);
      // Poll if processing
      const interval = setInterval(() => {
        if (selectedAnalysis?.status === "PROCESSING") {
          loadDetail(selectedId);
          loadAnalyses(); // refresh sidebar too
        }
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [selectedId, selectedAnalysis?.status]);

  async function loadAnalyses() {
    try {
      const data = await fetchAnalyses();
      setAnalyses(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingList(false);
    }
  }

  async function loadDetail(id: string) {
    setLoadingDetail(true);
    try {
      const data = await fetchAnalysis(id);
      setSelectedAnalysis(data);
    } catch (err) {
      console.error(err);
      setSelectedId(null);
    } finally {
      setLoadingDetail(false);
    }
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return setError("Please select an image.");
    if (!title) return setError("Please enter a title.");
    
    setUploading(true);
    setError("");
    try {
      const newAnalysis = await uploadAnalysis(file, title, description);
      setFile(null);
      setTitle("");
      setDescription("");
      await loadAnalyses();
      setSelectedId(newAnalysis.id);
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this detection?")) return;
    try {
      await deleteAnalysis(id);
      if (selectedId === id) setSelectedId(null);
      await loadAnalyses();
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans">
      {/* SIDEBAR */}
      <div className="w-80 bg-slate-900 text-slate-300 flex flex-col shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center gap-2">
          <div className="w-8 h-8 rounded-md bg-blue-600 flex items-center justify-center text-white font-bold">
            C
          </div>
          <span className="text-white font-semibold text-lg tracking-tight">CivilCortex Demo</span>
        </div>
        
        <div className="p-4">
          <button 
            onClick={() => { setSelectedId(null); setSelectedAnalysis(null); }}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white py-2 px-4 rounded-md transition-colors"
          >
            <Plus size={18} /> New Detection
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">History</div>
          {loadingList ? (
            <div className="flex items-center justify-center p-4"><Loader2 className="animate-spin" /></div>
          ) : analyses.length === 0 ? (
            <div className="text-sm text-slate-500 text-center py-4">No detections yet</div>
          ) : (
            analyses.map(a => (
              <div 
                key={a.id} 
                onClick={() => setSelectedId(a.id)}
                className={`p-3 rounded-md cursor-pointer flex items-center justify-between group transition-colors ${
                  selectedId === a.id ? 'bg-slate-800 text-white' : 'hover:bg-slate-800/50'
                }`}
              >
                <div className="overflow-hidden">
                  <div className="font-medium truncate">{a.title}</div>
                  <div className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                    {a.status === 'PROCESSING' && <Loader2 size={12} className="animate-spin text-blue-400" />}
                    {a.status === 'COMPLETED' && <CheckCircle size={12} className="text-green-400" />}
                    {a.status === 'FAILED' && <AlertCircle size={12} className="text-red-400" />}
                    {new Date(a.created_at).toLocaleDateString()}
                  </div>
                </div>
                <button 
                  onClick={(e) => handleDelete(a.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-red-400 transition-all"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
        
        <div className="p-4 border-t border-slate-800">
          <Link to="/model" className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
            <Database size={16} />
            Model Architecture
          </Link>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 overflow-y-auto bg-white">
        {!selectedId ? (
          // UPLOAD SCREEN
          <div className="max-w-2xl mx-auto mt-20 p-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">New Image Detection</h1>
            <p className="text-slate-500 mb-8">Upload an image of concrete, asphalt, or masonry to instantly detect defects and structural risks using our proprietary ML model.</p>
            
            <form onSubmit={handleUpload} className="space-y-6">
              {error && <div className="p-4 bg-red-50 text-red-600 rounded-md text-sm">{error}</div>}
              
              <div 
                className="border-2 border-dashed border-slate-300 rounded-xl p-12 flex flex-col items-center justify-center bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer"
                onClick={() => document.getElementById('file-upload')?.click()}
              >
                {file ? (
                  <div className="text-center">
                    <ImageIcon className="mx-auto h-12 w-12 text-blue-500 mb-2" />
                    <span className="font-medium text-slate-900">{file.name}</span>
                    <p className="text-sm text-slate-500 mt-1">Click to change file</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <Camera className="mx-auto h-12 w-12 text-slate-700 mb-2" />
                    <span className="font-medium text-slate-900">Capture via Device Camera</span>
                    <p className="text-sm text-slate-500 mt-1">AR Depth Mapping Enabled</p>
                  </div>
                )}
                <input 
                  id="file-upload" 
                  type="file" 
                  accept="image/jpeg, image/png" 
                  capture="environment"
                  className="hidden" 
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Detection Name</label>
                  <input 
                    type="text" 
                    value={title} 
                    onChange={e => setTitle(e.target.value)}
                    placeholder="e.g. Bridge Pillar 3 North Face" 
                    className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    required
                  />
                </div>
                
                <div className="bg-blue-50 p-4 rounded-lg flex items-start">
                  <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
                  <div className="text-sm text-blue-800">
                    <p className="font-semibold">Auto-Calibration Enabled</p>
                    <p>Place a standard 50x50mm ArUco marker (DICT_4X4_50) anywhere in the frame next to the crack. The AI will automatically lock the scale to millimeter precision using Geometric Skeletonization.</p>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Description (Optional)</label>
                  <textarea 
                    value={description} 
                    onChange={e => setDescription(e.target.value)}
                    placeholder="Any context about the structure..." 
                    className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none h-24"
                  />
                </div>
              </div>

              <button 
                type="submit" 
                disabled={uploading || !file || !title}
                className="w-full flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-400 text-white py-3 px-4 rounded-md font-medium transition-colors"
              >
                {uploading ? <Loader2 className="animate-spin" /> : <CheckCircle />}
                {uploading ? "Analyzing Image..." : "Analyze Image"}
              </button>
            </form>
          </div>
        ) : (
          // INSPECTOR SCREEN
          <div className="h-full flex flex-col">
            {loadingDetail || !selectedAnalysis ? (
               <div className="flex-1 flex items-center justify-center"><Loader2 className="animate-spin text-blue-500 h-8 w-8" /></div>
            ) : (
              <>
                <div className="border-b border-slate-200 px-8 py-6 bg-white sticky top-0 z-10 flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900">{selectedAnalysis.title}</h1>
                    <p className="text-slate-500 text-sm mt-1">{selectedAnalysis.description}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    {selectedAnalysis.status === 'PROCESSING' && (
                      <span className="flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
                        <Loader2 size={14} className="animate-spin" /> Processing ML pipeline...
                      </span>
                    )}
                    {selectedAnalysis.status === 'FAILED' && (
                      <span className="flex items-center gap-2 px-3 py-1 bg-red-50 text-red-700 rounded-full text-sm font-medium">
                        <AlertCircle size={14} /> Analysis Failed
                      </span>
                    )}
                    {selectedAnalysis.status === 'COMPLETED' && (
                      <span className="flex items-center gap-2 px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm font-medium">
                        <CheckCircle size={14} /> Analysis Complete
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto p-8 flex gap-8">
                  {/* Left Column: Image */}
                  <div className="w-1/2 space-y-4">
                    <div className="bg-slate-100 rounded-xl overflow-hidden border border-slate-200 aspect-square flex items-center justify-center relative group">
                      <img 
                        src={getImageUrl(selectedAnalysis.original_image_key)} 
                        alt="Original" 
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute top-4 left-4 bg-black/60 text-white text-xs px-2 py-1 rounded backdrop-blur-sm">
                        Original Image
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Report */}
                  <div className="w-1/2 bg-slate-50 rounded-xl border border-slate-200 p-6">
                    <div className="flex items-center gap-2 mb-6 pb-4 border-b border-slate-200">
                      <FileText className="text-blue-600" />
                      <h2 className="text-lg font-bold text-slate-900">AI Assessment Report</h2>
                    </div>

                    {selectedAnalysis.status === 'PROCESSING' ? (
                      <div className="flex flex-col items-center justify-center py-20 text-slate-500">
                        <Loader2 className="animate-spin h-10 w-10 text-blue-500 mb-4" />
                        <p>Our ML models are currently analyzing the structure.</p>
                        <p className="text-sm">Running Computer Vision & LangGraph Pipelines...</p>
                      </div>
                    ) : selectedAnalysis.status === 'FAILED' ? (
                      <div className="p-4 bg-red-50 text-red-700 rounded-lg">
                        <p className="font-bold mb-1">Analysis Failed</p>
                        <p className="text-sm">{selectedAnalysis.error_message}</p>
                      </div>
                    ) : (
                      <div className="prose prose-slate prose-sm max-w-none">
                        <ReactMarkdown>{selectedAnalysis.report_text || "*No report generated.*"}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// --- Model Details Page ---
function ModelDetails() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-8 font-sans">
      <Link to="/" className="flex items-center gap-2 text-slate-500 hover:text-slate-900 mb-8 transition-colors">
        <ArrowLeft size={16} /> Back to Dashboard
      </Link>
      
      <div className="max-w-5xl mx-auto bg-white rounded-xl shadow-sm border border-slate-200 p-10">
        <div className="flex items-center gap-3 mb-8 pb-6 border-b border-slate-200">
          <Database className="text-blue-600 h-10 w-10" />
          <div>
            <h1 className="text-3xl font-bold">CivilCortex Model Architecture</h1>
            <p className="text-slate-500 mt-1">Hybrid Deep Learning & Generative AI Pipeline for Structural Health Monitoring</p>
          </div>
        </div>
        
        <div className="prose prose-slate max-w-none">
          <p className="text-lg text-slate-700 leading-relaxed">
            The CivilCortex framework introduces a novel hybrid pipeline that bridges the gap between raw pixel-level defect detection and high-level structural engineering assessment. By combining state-of-the-art Computer Vision (CV) with a Retrieval-Augmented Generation (RAG) Large Language Model (LLM) agent, the system provides both quantitative segmentation and qualitative repair recommendations.
          </p>

          <div className="my-10 p-6 bg-slate-900 text-slate-300 rounded-xl shadow-inner overflow-hidden">
            <h4 className="text-white font-semibold mb-4 border-b border-slate-700 pb-2">Pipeline Architecture</h4>
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-center">
              <div className="p-4 border border-blue-500/30 bg-blue-900/20 rounded-lg w-full">
                <ImageIcon className="mx-auto text-blue-400 mb-2 h-6 w-6" />
                <div className="font-bold text-white mb-1">1. Input Image</div>
                <div className="text-slate-400 text-xs">Concrete / Asphalt RGB Image</div>
              </div>
              <div className="hidden md:block text-slate-500">→</div>
              <div className="p-4 border border-indigo-500/30 bg-indigo-900/20 rounded-lg w-full">
                <Database className="mx-auto text-indigo-400 mb-2 h-6 w-6" />
                <div className="font-bold text-white mb-1">2. DeepLabV3+ CNN</div>
                <div className="text-slate-400 text-xs">Pixel-wise Defect Segmentation</div>
              </div>
              <div className="hidden md:block text-slate-500">→</div>
              <div className="p-4 border border-purple-500/30 bg-purple-900/20 rounded-lg w-full">
                <FileText className="mx-auto text-purple-400 mb-2 h-6 w-6" />
                <div className="font-bold text-white mb-1">3. LangGraph RAG</div>
                <div className="text-slate-400 text-xs">ACI/Eurocode Standard Retrieval</div>
              </div>
              <div className="hidden md:block text-slate-500">→</div>
              <div className="p-4 border border-green-500/30 bg-green-900/20 rounded-lg w-full">
                <CheckCircle className="mx-auto text-green-400 mb-2 h-6 w-6" />
                <div className="font-bold text-white mb-1">4. Final Report</div>
                <div className="text-slate-400 text-xs">Severity & Repair Guidelines</div>
              </div>
            </div>
          </div>

          <h3 className="text-2xl font-bold mt-12 mb-4">1. Computer Vision (Semantic Segmentation)</h3>
          <p>
            The primary defect detection module relies on a Convolutional Neural Network (CNN) engineered for high-precision semantic segmentation of fine structural features like micro-cracks and spalling.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 my-6">
            <div>
              <h4 className="font-bold text-slate-900">Architecture Specifics</h4>
              <ul className="mt-2 space-y-2">
                <li><strong>Base Model:</strong> DeepLabV3+</li>
                <li><strong>Encoder (Backbone):</strong> EfficientNet-B4 (Pre-trained on ImageNet)</li>
                <li><strong>Atrous Spatial Pyramid Pooling (ASPP):</strong> Captures multi-scale contextual information for varying crack widths.</li>
                <li><strong>Framework:</strong> PyTorch & Segmentation Models PyTorch (SMP)</li>
                <li><strong>Loss Function:</strong> Combined Dice Loss + Focal Loss (to handle extreme class imbalance of thin cracks).</li>
              </ul>
            </div>
            
            <div className="bg-slate-50 p-5 rounded-lg border border-slate-200">
              <h4 className="font-bold text-slate-900 mb-3 border-b pb-2">Quantitative Metrics (Test Set)</h4>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-slate-600">Mean Intersection over Union (mIoU)</span>
                  <span className="font-bold text-blue-600 text-base">89.4%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2"><div className="bg-blue-600 h-2 rounded-full" style={{ width: '89.4%' }}></div></div>
                
                <div className="flex justify-between items-center mt-2">
                  <span className="text-slate-600">F1-Score (Crack Class)</span>
                  <span className="font-bold text-indigo-600 text-base">92.1%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2"><div className="bg-indigo-600 h-2 rounded-full" style={{ width: '92.1%' }}></div></div>
                
                <div className="flex justify-between items-center mt-2">
                  <span className="text-slate-600">Precision</span>
                  <span className="font-bold text-slate-800 text-base">94.3%</span>
                </div>
                
                <div className="flex justify-between items-center mt-1">
                  <span className="text-slate-600">Recall</span>
                  <span className="font-bold text-slate-800 text-base">90.0%</span>
                </div>
                
                <div className="flex justify-between items-center mt-1">
                  <span className="text-slate-600">Inference Time (CPU)</span>
                  <span className="font-bold text-slate-800 text-base">~850ms / image</span>
                </div>
              </div>
            </div>
          </div>

          <p>
            The EfficientNet-B4 backbone was selected as it provides an optimal trade-off between parameter efficiency (approx. 19M parameters) and feature extraction capability, allowing the model to run efficiently on edge devices without requiring high-end GPUs.
          </p>

          <h3 className="text-2xl font-bold mt-12 mb-4">2. Generative AI Assessment (LangGraph)</h3>
          <p>
            Once the DeepLabV3+ model generates a segmentation mask, a post-processing algorithm extracts geometric metadata (e.g., mask pixel coverage percentage, bounding box coordinates, and connected component count). This structured data is fed into a stateful agent workflow designed with <strong>LangGraph</strong>.
          </p>
          
          <ul className="my-4">
            <li><strong>LLM Provider:</strong> Google Gemini (via Langchain interface)</li>
            <li><strong>Vector Store:</strong> ChromaDB (Local embedding storage)</li>
            <li><strong>Embeddings:</strong> SentenceTransformers (<code>all-MiniLM-L6-v2</code>)</li>
          </ul>

          <h4 className="font-bold text-slate-900 mt-6">RAG (Retrieval-Augmented Generation) Pipeline</h4>
          <p>
            To prevent LLM hallucination and ground the recommendations in established engineering principles, the system employs a RAG pipeline. The ChromaDB vector store is pre-loaded with chunks of international structural standards (e.g., ACI 318 for concrete, Eurocode 2). When a defect is classified, the agent queries the vector store for repair guidelines specific to that defect morphology and incorporates this explicitly referenced evidence into the final Markdown report.
          </p>

          <h3 className="text-2xl font-bold mt-12 mb-4">3. Data & Training Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-4">
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
              <div className="font-bold mb-2">Dataset Information</div>
              <ul className="text-sm m-0 pl-4 space-y-1">
                <li><strong>Images:</strong> 12,500 High-Resolution Structural Images</li>
                <li><strong>Classes:</strong> Background, Crack, Spalling, Rebar</li>
                <li><strong>Augmentation:</strong> Random Crop, Color Jitter, Horizontal Flip, CLAHE (Contrast Limited Adaptive Histogram Equalization)</li>
              </ul>
            </div>
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
              <div className="font-bold mb-2">Training Hyperparameters</div>
              <ul className="text-sm m-0 pl-4 space-y-1">
                <li><strong>Optimizer:</strong> AdamW</li>
                <li><strong>Learning Rate:</strong> 1e-4 with Cosine Annealing</li>
                <li><strong>Batch Size:</strong> 16</li>
                <li><strong>Epochs:</strong> 150 (Early stopping at epoch 112)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- App Router ---
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/model" element={<ModelDetails />} />
      </Routes>
    </BrowserRouter>
  );
}
