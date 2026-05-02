export function generateMigrations(beforeTables, afterTables) {
  const scripts = [];
  
  // Find new tables
  afterTables.forEach(afterTable => {
    const beforeTable = beforeTables.find(t => t.name === afterTable.name);
    
    if (!beforeTable) {
      // It's a new table
      let script = `CREATE TABLE ${afterTable.name} (\n`;
      const colDefs = afterTable.columns.map(col => {
        let def = `  ${col.name} ${col.type}`;
        return def;
      });
      script += colDefs.join(',\n');
      
      // Add Foreign Keys
      afterTable.columns.filter(col => col.isFk).forEach(col => {
         script += `,\n  FOREIGN KEY (${col.name}) REFERENCES ${col.references}(id)`;
      });
      
      script += '\n);';
      scripts.push(script);
    } else {
      // Existing table, check for modifications
      const columnsToAdd = [];
      const columnsToDrop = [];
      
      afterTable.columns.forEach(aCol => {
        const bCol = beforeTable.columns.find(c => c.name === aCol.name);
        if (!bCol) {
          columnsToAdd.push(`ADD COLUMN ${aCol.name} ${aCol.type}`);
        }
      });
      
      beforeTable.columns.forEach(bCol => {
        const aCol = afterTable.columns.find(c => c.name === bCol.name);
        if (!aCol) {
          columnsToDrop.push(`DROP COLUMN ${bCol.name}`);
        }
      });
      
      if (columnsToAdd.length > 0 || columnsToDrop.length > 0) {
        let script = `ALTER TABLE ${beforeTable.name}\n`;
        const actions = [...columnsToAdd, ...columnsToDrop];
        script += '  ' + actions.join(',\n  ') + ';';
        scripts.push(script);
      }
    }
  });

  return scripts.length > 0 ? scripts.join('\n\n') : '-- No migrations needed';
}
