export function parseSql(sqlString) {
  // A very basic SQL parser to extract CREATE TABLE statements
  const tables = [];
  
  // Normalize whitespace
  const normalizedSql = sqlString.replace(/\n/g, ' ').replace(/\s+/g, ' ');
  
  // Basic regex to find CREATE TABLE blocks
  const tableRegex = /CREATE TABLE\s+(?:IF NOT EXISTS\s+)?`?(\w+)`?\s*\((.*?)\)(?:;|$)/gi;
  let match;
  
  while ((match = tableRegex.exec(normalizedSql)) !== null) {
    const tableName = match[1];
    const columnsStr = match[2];
    
    // Split by comma, but naive approach fails with functions like DECIMAL(10,2)
    // Using a more robust split that ignores commas inside parentheses
    const columnParts = [];
    let currentPart = '';
    let parenCount = 0;
    
    for (let i = 0; i < columnsStr.length; i++) {
      const char = columnsStr[i];
      if (char === '(') parenCount++;
      if (char === ')') parenCount--;
      
      if (char === ',' && parenCount === 0) {
        columnParts.push(currentPart.trim());
        currentPart = '';
      } else {
        currentPart += char;
      }
    }
    if (currentPart.trim()) {
      columnParts.push(currentPart.trim());
    }
    
    const columns = [];
    columnParts.forEach(part => {
      // Check for PRIMARY KEY constraint at table level
      if (part.toUpperCase().startsWith('PRIMARY KEY')) return; // Simplified: ignore table-level PK for now
      
      // Parse column name and type
      const parts = part.trim().split(/\s+/);
      const name = parts[0].replace(/`/g, '');
      const type = parts.length > 1 ? parts.slice(1).join(' ') : 'VARCHAR(255)';
      
      const isPk = part.toUpperCase().includes('PRIMARY KEY');
      
      columns.push({
        name,
        type,
        isPk
      });
    });
    
    tables.push({
      name: tableName,
      columns
    });
  }
  
  return tables;
}
