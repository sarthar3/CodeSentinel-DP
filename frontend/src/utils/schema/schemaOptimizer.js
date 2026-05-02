export function optimizeSchema(tables) {
  const optimizedTables = JSON.parse(JSON.stringify(tables)); // Deep clone
  const newTables = [];

  optimizedTables.forEach(table => {
    const columnsToRemove = [];
    const repeatingGroups = new Map(); // Prefix -> [columns]
    
    // Check for ID
    const hasId = table.columns.some(col => col.name.toLowerCase() === 'id' || col.isPk);
    if (!hasId) {
        table.columns.unshift({ name: 'id', type: 'INT AUTO_INCREMENT PRIMARY KEY', isPk: true, isNew: true });
    }

    table.columns.forEach(col => {
      const lowerName = col.name.toLowerCase();

      // Heuristic 1: Array-like string columns (e.g., skills, tags) -> Many-to-Many or One-to-Many
      if (lowerName === 'skills' || lowerName === 'tags' || lowerName.endsWith('_list')) {
        columnsToRemove.push(col.name);
        const newTableName = col.name.charAt(0).toUpperCase() + col.name.slice(1);
        newTables.push({
          name: newTableName,
          isNewTable: true,
          columns: [
            { name: 'id', type: 'INT AUTO_INCREMENT PRIMARY KEY', isPk: true },
            { name: `${table.name.toLowerCase()}_id`, type: 'INT', isFk: true, references: table.name },
            { name: 'value', type: 'VARCHAR(255)' }
          ]
        });
      }

      // Heuristic 2: Repeating columns (e.g., address1, address2, address3)
      const match = col.name.match(/^(.*?)(\d+)$/);
      if (match) {
        const prefix = match[1];
        if (!repeatingGroups.has(prefix)) {
          repeatingGroups.set(prefix, []);
        }
        repeatingGroups.get(prefix).push(col);
      }
    });

    // Process repeating groups
    repeatingGroups.forEach((cols, prefix) => {
      if (cols.length > 1) {
        // Remove old repeating columns
        cols.forEach(col => columnsToRemove.push(col.name));
        
        // Create new table
        const newTableName = table.name + '_' + prefix.charAt(0).toUpperCase() + prefix.slice(1) + 's';
        newTables.push({
          name: newTableName,
          isNewTable: true,
          columns: [
            { name: 'id', type: 'INT AUTO_INCREMENT PRIMARY KEY', isPk: true },
            { name: `${table.name.toLowerCase()}_id`, type: 'INT', isFk: true, references: table.name },
            { name: 'value', type: 'VARCHAR(255)' }
          ]
        });
      }
    });

    // Remove old columns
    table.columns = table.columns.filter(col => !columnsToRemove.includes(col.name));
  });

  return [...optimizedTables, ...newTables];
}
