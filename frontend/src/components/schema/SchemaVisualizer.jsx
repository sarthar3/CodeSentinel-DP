import React from 'react';
import { Key, Link } from 'lucide-react';

const TableCard = ({ table, isAfter }) => {
  return (
    <div className="mb-6">
      <div className="text-xs text-black/50 mb-2 uppercase flex justify-between">
        <span>{table.name}</span>
        {table.isNewTable && isAfter && <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-[10px] font-bold">NEW</span>}
      </div>
      <div className="bg-white/50 rounded border border-beige-300 overflow-hidden">
        {table.columns.map((col, idx) => {
          let indColor = "bg-white";
          if (col.isPk) indColor = "bg-orange-400";
          if (col.isFk) indColor = "bg-green-500";

          return (
            <div key={idx} className="flex items-center justify-between p-3 border-b border-beige-200 last:border-0 hover:bg-beige-50 transition-colors">
              <span className="flex items-center gap-2 text-sm font-medium">
                <span className={`w-2 h-2 rounded-full ${indColor} border border-black/10`}></span>
                {col.name}
                {col.isPk && <Key size={12} className="text-orange-500" />}
                {col.isFk && <Link size={12} className="text-green-600" />}
              </span>
              <span className="text-xs text-black/40 font-mono">{col.type}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default function SchemaVisualizer({ beforeTables, afterTables }) {
  if (!beforeTables.length && !afterTables.length) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <div className="card">
        <div className="card-header">
          <span>ORIGINAL SCHEMA</span>
          <span className="card-dots">•••</span>
        </div>
        <div className="p-1">
          {beforeTables.map((t, i) => <TableCard key={i} table={t} isAfter={false} />)}
        </div>
        <div className="card-footer">
          <div className="flex gap-4 text-xs opacity-70">
             <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-white border border-black/10"></span> Column</span>
             <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-orange-400 border border-black/10"></span> Primary Key</span>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span>OPTIMIZED SCHEMA</span>
          <span className="card-dots">•••</span>
        </div>
        <div className="p-1">
          {afterTables.map((t, i) => <TableCard key={i} table={t} isAfter={true} />)}
        </div>
        <div className="card-footer">
          <div className="flex gap-4 text-xs opacity-70">
             <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-white border border-black/10"></span> Column</span>
             <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-green-500 border border-black/10"></span> Foreign Key</span>
             <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-orange-400 border border-black/10"></span> Primary Key</span>
          </div>
        </div>
      </div>
    </div>
  );
}
