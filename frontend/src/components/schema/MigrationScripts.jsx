import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

export default function MigrationScripts({ scripts }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(scripts);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!scripts) return null;

  return (
    <div className="card">
      <div className="card-header">
        <span>MIGRATION SCRIPTS</span>
        <button 
          onClick={handleCopy}
          className="bg-beige-300 hover:bg-beige-400 text-black px-4 py-1.5 rounded flex items-center gap-2 text-sm font-semibold transition-colors border-none"
        >
          {copied ? <Check size={14} className="text-green-600" /> : <Copy size={14} />}
          {copied ? 'COPIED' : 'COPY SQL'}
        </button>
      </div>
      <div className="bg-beige-100 p-6 rounded-lg font-mono text-sm whitespace-pre overflow-x-auto text-black/80 border border-beige-300">
        {scripts}
      </div>
      <div className="card-footer">
        <span className="text-black/50">Apply these to reach the optimized state.</span>
        <span className="card-dots">•••</span>
      </div>
    </div>
  );
}
