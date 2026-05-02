import React from 'react';
import { Play, Database } from 'lucide-react';

const DEMO_SQL = `CREATE TABLE Employee (
  id INT,
  name VARCHAR(100),
  skills VARCHAR(255),
  tags VARCHAR(255),
  address1 VARCHAR(100),
  address2 VARCHAR(100),
  address3 VARCHAR(100)
);

CREATE TABLE Projects (
  project_id INT,
  project_name VARCHAR(100),
  technologies_list VARCHAR(255)
);`;

export default function SqlInputEditor({ sql, setSql, onAnalyze }) {
  const handleLoadDemo = () => {
    setSql(DEMO_SQL);
  };

  return (
    <div className="card h-full flex flex-col">
      <div className="card-header flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span>SCHEMA INPUT</span>
          <span className="card-dots">•••</span>
        </div>
        <div className="flex items-center gap-2 normal-case tracking-normal">
          <button 
            onClick={handleLoadDemo}
            className="flex items-center gap-2 px-3 py-1 bg-white border border-beige-300 rounded hover:bg-beige-50 text-sm transition-colors text-black font-medium"
          >
            <Database size={14} className="text-black" />
            Load Demo
          </button>
          <button 
            onClick={onAnalyze}
            className="flex items-center gap-2 px-3 py-1 bg-beige-300 border border-beige-300 rounded hover:bg-beige-400 text-sm transition-colors text-black font-medium"
          >
            <Play size={14} className="text-black" />
            Optimize Schema
          </button>
        </div>
      </div>
      
      <div className="flex-1 min-h-[300px]">
        <textarea 
          className="w-full h-full p-6 bg-beige-100 border-none rounded font-mono text-sm resize-none focus:ring-0 text-black/80 placeholder-black/30"
          value={sql}
          onChange={(e) => setSql(e.target.value)}
          placeholder="CREATE TABLE Users (&#10;  id INT,&#10;  name VARCHAR(100),&#10;  skills VARCHAR(255),&#10;  address1 VARCHAR(100),&#10;  address2 VARCHAR(100)&#10;);"
          spellCheck="false"
        />
      </div>
    </div>
  );
}
