import React, { useState } from 'react';
import { Upload, FileText, Sparkles, Loader2, BrainCircuit, Table } from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

export default function ModelSuggester() {
  const [file, setFile] = useState(null);
  const [description, setDescription] = useState('');
  const [extraInput, setExtraInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleAnalyze = async () => {
    if (!file || !description.trim()) return;
    setIsAnalyzing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', description);
    formData.append('extra_input', extraInput);

    try {
      const response = await axios.post('http://localhost:8000/api/suggester/suggest', formData);
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Error suggesting model");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col h-full animate-in fade-in duration-500">
      {/* Header */}
      <div className="bg-beige-200 border-b border-beige-300 p-6">
        <h1 className="text-2xl font-bold mb-2">AI Model Suggester</h1>
        <p className="text-black">
          Upload preprocessed data and explain your project to receive AI-powered algorithm recommendations.
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-6xl mx-auto grid grid-cols-1 xl:grid-cols-2 gap-8">
          
          <div className="space-y-6">
            <div className="card">
              <div className="card-header">
                <span>INPUT DATA & CONTEXT</span>
              </div>
              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-bold text-black/40 uppercase mb-2">Preprocessed Dataset (CSV)</label>
                  <div className="flex items-center gap-4">
                    <input 
                      type="file" 
                      accept=".csv" 
                      onChange={handleFileChange}
                      className="hidden" 
                      id="data-upload"
                    />
                    <label 
                      htmlFor="data-upload"
                      className="flex-1 bg-beige-100 border border-beige-300 p-4 rounded-xl cursor-pointer hover:bg-beige-200 transition-colors flex items-center justify-between"
                    >
                      <span className="text-sm font-medium">{file ? file.name : "Choose CSV..."}</span>
                      <Upload size={18} className="text-black/40" />
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-black/40 uppercase mb-2">Project Description</label>
                  <textarea 
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe what you want to achieve with this data (e.g., 'I want to predict if a user will churn next month based on their activity')."
                    className="w-full h-40 bg-beige-100 border border-beige-300 rounded-xl p-4 text-sm focus:ring-0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-black/40 uppercase mb-2">Additional Requirements (Optional)</label>
                  <input 
                    type="text"
                    value={extraInput}
                    onChange={(e) => setExtraInput(e.target.value)}
                    placeholder="e.g., 'Needs to be interpretable', 'Must run on mobile'"
                    className="w-full bg-beige-100 border border-beige-300 rounded-xl p-4 text-sm focus:ring-0"
                  />
                </div>
              </div>
              <div className="card-footer border-t-0 pt-0">
                <button 
                  onClick={handleAnalyze}
                  disabled={!file || !description || isAnalyzing}
                  className="btn-primary w-full justify-center disabled:opacity-50"
                >
                  {isAnalyzing ? <Loader2 className="animate-spin" /> : <Sparkles size={18} />}
                  {isAnalyzing ? "ANALYZING..." : "GET RECOMMENDATIONS"}
                </button>
              </div>
            </div>

            {result && result.summary && (
              <div className="card">
                <div className="card-header">
                  <span>DATASET PROFILE</span>
                </div>
                <div className="p-6">
                   <div className="flex gap-8 mb-6">
                      <div className="flex flex-col">
                        <span className="text-3xl font-bold">{result.summary.shape[0]}</span>
                        <span className="text-xs text-black/40 uppercase">Rows</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-3xl font-bold">{result.summary.shape[1]}</span>
                        <span className="text-xs text-black/40 uppercase">Columns</span>
                      </div>
                   </div>
                   <div>
                     <span className="text-xs font-bold text-black/40 uppercase block mb-3">Sample View</span>
                     <div className="overflow-x-auto">
                        <table className="w-full text-xs border-collapse">
                          <thead>
                            <tr className="bg-beige-100">
                              {Object.keys(result.summary.sample[0]).map(k => (
                                <th key={k} className="p-2 border border-beige-300 text-left">{k}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {result.summary.sample.map((row, i) => (
                              <tr key={i}>
                                {Object.values(row).map((v, j) => (
                                  <td key={j} className="p-2 border border-beige-300 max-w-[150px] truncate">{String(v)}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                     </div>
                   </div>
                </div>
              </div>
            )}
          </div>

          <div className="space-y-6">
            {!result && !isAnalyzing && (
              <div className="h-full flex flex-col items-center justify-center p-12 text-center text-black/20">
                <BrainCircuit size={80} className="mb-4" />
                <h3 className="text-xl font-bold">AI Recommendation Engine</h3>
                <p className="max-w-xs text-sm mt-2">Upload your data and provide context to see the magic happen.</p>
              </div>
            )}

            {isAnalyzing && (
              <div className="h-full flex flex-col items-center justify-center p-12 text-center">
                <Loader2 size={48} className="animate-spin text-green-600 mb-4" />
                <h3 className="text-xl font-bold">Processing Dataset...</h3>
                <p className="text-sm text-black/60 mt-2">Gemini is analyzing your data features and project goals.</p>
              </div>
            )}

            {result && result.recommendation && (
              <div className="space-y-6">
                {/* Metrics Summary */}
                {result.metrics && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="card bg-green-50 border-green-200">
                      <div className="p-6">
                        <span className="text-xs font-bold text-green-700 uppercase block mb-1">Estimated Accuracy</span>
                        <div className="flex items-end gap-2">
                          <span className="text-4xl font-black text-green-900">{(result.metrics.accuracy * 100).toFixed(1)}%</span>
                          <span className="text-sm text-green-700/60 mb-1">Target</span>
                        </div>
                        <div className="mt-4 h-2 w-full bg-green-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-green-600 rounded-full transition-all duration-1000" 
                            style={{ width: `${result.metrics.accuracy * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="card bg-beige-200">
                      <div className="p-4">
                        <span className="text-xs font-bold text-black/40 uppercase block mb-3">Confusion Matrix (Estim.)</span>
                        <div className="grid grid-cols-3 gap-2 text-center">
                          <div className="bg-beige-300 rounded p-2 flex flex-col">
                            <span className="text-xs text-black/40">TP</span>
                            <span className="font-bold">{result.metrics.confusion_matrix.values?.[0]?.[0] || 0}</span>
                          </div>
                          <div className="bg-red-100 rounded p-2 flex flex-col">
                            <span className="text-xs text-red-400">FP</span>
                            <span className="font-bold">{result.metrics.confusion_matrix.values?.[0]?.[1] || 0}</span>
                          </div>
                          <div className="bg-red-100 rounded p-2 flex flex-col">
                            <span className="text-xs text-red-400">FN</span>
                            <span className="font-bold">{result.metrics.confusion_matrix.values?.[1]?.[0] || 0}</span>
                          </div>
                          <div className="bg-beige-300 rounded p-2 flex flex-col col-start-2">
                            <span className="text-xs text-black/40">TN</span>
                            <span className="font-bold">{result.metrics.confusion_matrix.values?.[1]?.[1] || 0}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Alternatives */}
                {result.metrics && result.metrics.alternatives && (
                   <div className="card">
                     <div className="card-header border-b">
                       <span>ALTERNATIVE MODEL COMPARISON</span>
                     </div>
                     <div className="p-4 space-y-3">
                        {result.metrics.alternatives.map((alt, idx) => (
                          <div key={idx} className="flex items-center justify-between p-3 bg-beige-100 rounded-xl">
                            <div className="flex flex-col">
                              <span className="font-bold text-sm">{alt.name}</span>
                              <span className="text-[10px] text-black/40 uppercase">Benchmark</span>
                            </div>
                            <span className="text-sm font-mono bg-beige-300 px-2 py-1 rounded">{(alt.accuracy * 100).toFixed(0)}%</span>
                          </div>
                        ))}
                     </div>
                   </div>
                )}

                <div className="card h-fit animate-in slide-in-from-right duration-500">
                  <div className="card-header bg-green-50">
                    <div className="flex items-center gap-2">
                      <Sparkles size={16} className="text-green-600" />
                      <span>AI ARCHITECTURAL RATIONALE</span>
                    </div>
                  </div>
                  <div className="p-8 prose prose-sm max-w-none text-black/80">
                    <ReactMarkdown>{result.recommendation}</ReactMarkdown>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-100 border border-red-200 text-red-700 p-4 rounded-xl">
                {error}
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
