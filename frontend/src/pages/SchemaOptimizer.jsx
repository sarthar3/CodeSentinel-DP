import React, { useState } from 'react';
import { Database } from 'lucide-react';
import SqlInputEditor from '../components/schema/SqlInputEditor';
import SchemaVisualizer from '../components/schema/SchemaVisualizer';
import MigrationScripts from '../components/schema/MigrationScripts';
import { parseSql } from '../utils/schema/sqlParser';
import { optimizeSchema } from '../utils/schema/schemaOptimizer';
import { generateMigrations } from '../utils/schema/migrationGenerator';

export default function SchemaOptimizer() {
  const [sql, setSql] = useState('');
  const [beforeTables, setBeforeTables] = useState([]);
  const [afterTables, setAfterTables] = useState([]);
  const [migrations, setMigrations] = useState('');

  const handleAnalyze = () => {
    if (!sql.trim()) return;
    try {
      const parsedTables = parseSql(sql);
      const optimized = optimizeSchema(parsedTables);
      const scripts = generateMigrations(parsedTables, optimized);
      
      setBeforeTables(parsedTables);
      setAfterTables(optimized);
      setMigrations(scripts);
    } catch (err) {
      console.error("Error analyzing SQL:", err);
    }
  };

  return (
    <div className="flex flex-col h-full animate-in fade-in duration-500">
      {/* Header */}
      <div className="bg-beige-200 border-b border-beige-300 p-6">
        <h1 className="text-2xl font-bold mb-2">DB Schema Optimizer Agent</h1>
        <p className="text-black">
          Analyze and normalize SQL database schemas with AI-powered recommendations.
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
        <SqlInputEditor sql={sql} setSql={setSql} onAnalyze={handleAnalyze} />
        
        {beforeTables.length > 0 && (
          <div className="card">
            <div className="card-header">
              <span>OPTIMIZATION STATS</span>
              <span className="card-dots">•••</span>
            </div>
            <div className="flex gap-12 mb-8 px-2">
              <div className="flex flex-col">
                <div className="text-3xl font-bold flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-black/10 border border-black/5"></span>
                  {beforeTables.length}
                </div>
                <div className="text-xs text-black/40 uppercase tracking-wider font-semibold">Original Tables</div>
              </div>
              <div className="flex flex-col">
                <div className="text-3xl font-bold flex items-center gap-2 text-green-600">
                  <span className="w-3 h-3 rounded-full bg-green-500"></span>
                  {afterTables.length}
                </div>
                <div className="text-xs text-black/40 uppercase tracking-wider font-semibold">Optimized Tables</div>
              </div>
            </div>
            
            {/* Visual timeline representation */}
            <div className="h-24 border-b border-beige-300 relative mx-2">
               <div className="absolute bottom-5 left-[10%] w-[80%] h-0.5 bg-green-500"></div>
               <div className="absolute bottom-4 left-[20%] w-3 h-3 rounded-full bg-white border-2 border-black/10"></div>
               <div className="absolute bottom-4 left-[80%] w-3 h-3 rounded-full bg-orange-400 border-2 border-black/10"></div>
            </div>
            
            <div className="card-footer">
              <div className="flex gap-4 text-xs opacity-70">
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-white border border-black/10"></span> Before</span>
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-green-500"></span> After</span>
                <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-orange-400"></span> Relations</span>
              </div>
              <div className="text-xs text-black/40">Total Columns: {afterTables.reduce((acc, t) => acc + t.columns.length, 0)}</div>
            </div>
          </div>
        )}
      </div>

      <SchemaVisualizer beforeTables={beforeTables} afterTables={afterTables} />
      
        {migrations && (
          <div className="mt-6">
            <MigrationScripts scripts={migrations} />
          </div>
        )}
      </div>
    </div>
  );
}
