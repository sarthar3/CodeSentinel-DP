import React, { useState } from 'react';
import { Upload, FileText, Download, Loader2, CheckCircle, Database } from 'lucide-react';
import axios from 'axios';

export default function DatasetCleaner() {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleProcess = async () => {
    if (!file) return;
    setIsProcessing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/cleaner/clean', formData);
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Error processing dataset");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = (filename) => {
    window.open(`http://localhost:8000/api/cleaner/download/${filename}`);
  };

  return (
    <div className="flex flex-col h-full animate-in fade-in duration-500">
      {/* Header */}
      <div className="bg-beige-200 border-b border-beige-300 p-6">
        <h1 className="text-2xl font-bold mb-2">Dataset Cleaner & Preprocessor</h1>
        <p className="text-black">
          Automated cleaning, handling missing values, and numerical encoding for ML readiness.
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          
          <div className="card">
            <div className="card-header">
              <span>UPLOAD DATASET</span>
              <span className="card-dots">•••</span>
            </div>
            <div className="p-8 flex flex-col items-center justify-center border-2 border-dashed border-beige-300 rounded-xl m-6 bg-beige-100/50">
              <Upload className="w-12 h-12 text-black/20 mb-4" />
              <p className="text-sm text-black/60 mb-4">Upload your raw CSV file to begin cleaning</p>
              <input 
                type="file" 
                accept=".csv" 
                onChange={handleFileChange}
                className="hidden" 
                id="dataset-upload"
              />
              <label 
                htmlFor="dataset-upload"
                className="bg-beige-300 hover:bg-beige-400 px-6 py-2 rounded-lg cursor-pointer transition-colors font-medium flex items-center gap-2"
              >
                <FileText size={18} />
                {file ? file.name : "Select CSV File"}
              </label>
            </div>
            <div className="card-footer border-t-0 pt-0">
               <button 
                onClick={handleProcess}
                disabled={!file || isProcessing}
                className="btn-primary w-full justify-center disabled:opacity-50"
               >
                 {isProcessing ? <Loader2 className="animate-spin" /> : <CheckCircle size={18} />}
                 {isProcessing ? "CLEANING DATA..." : "START PREPROCESSING"}
               </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-200 text-red-700 p-4 rounded-xl">
              {error}
            </div>
          )}

          {result && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card">
                <div className="card-header">
                  <span>PROCESSING SUMMARY</span>
                </div>
                <div className="p-6 space-y-4">
                  <div className="flex justify-between border-b border-beige-300 pb-2">
                    <span className="text-black/60">Original Shape</span>
                    <span className="font-mono">{result.original_shape[0]} x {result.original_shape[1]}</span>
                  </div>
                  <div className="flex justify-between border-b border-beige-300 pb-2">
                    <span className="text-black/60">Cleaned Shape</span>
                    <span className="font-mono">{result.cleaned_shape[0]} x {result.cleaned_shape[1]}</span>
                  </div>
                  <div>
                    <span className="text-xs font-bold text-black/40 uppercase block mb-2">Encoded Columns</span>
                    <div className="flex flex-wrap gap-2">
                      {result.categorical_columns.map(col => (
                        <span key={col} className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-medium">
                          {col}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card-header">
                  <span>OUTPUT FILES</span>
                </div>
                <div className="p-6 flex flex-col gap-4">
                  <button 
                    onClick={() => handleDownload(result.cleaned_csv)}
                    className="flex items-center justify-between p-4 bg-white border border-beige-300 rounded-xl hover:bg-beige-50 transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
                        <Download className="text-green-600" size={20} />
                      </div>
                      <div className="text-left">
                        <div className="font-bold">Numerical Dataset</div>
                        <div className="text-xs text-black/40">Cleaned & Encoded (CSV)</div>
                      </div>
                    </div>
                  </button>

                  <button 
                    onClick={() => handleDownload(result.preprocessor_pkl)}
                    className="flex items-center justify-between p-4 bg-white border border-beige-300 rounded-xl hover:bg-beige-50 transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-orange-100 rounded-lg group-hover:bg-orange-200 transition-colors">
                        <Database className="text-orange-600" size={20} />
                      </div>
                      <div className="text-left">
                        <div className="font-bold">Preprocessor Object</div>
                        <div className="text-xs text-black/40">LabelEncoders (.pkl)</div>
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
