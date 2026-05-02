import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'

function DebugApp() {
  const [loadStatus, setLoadStatus] = useState({})
  
  useEffect(() => {
    const checkComponents = async () => {
      const components = {
        Layout: () => import('./components/Layout'),
        ChatRAG: () => import('./pages/ChatRAG'),
        CodePorter: () => import('./pages/CodePorter'),
        QADashboard: () => import('./pages/QADashboard'),
        TriageDashboard: () => import('./pages/TriageDashboard'),
        CICDMonitor: () => import('./pages/CICDMonitor'),
      }
      
      const status = {}
      for (const [name, loader] of Object.entries(components)) {
        try {
          await loader()
          status[name] = '✅ OK'
        } catch (error) {
          status[name] = `❌ Error: ${error.message}`
        }
      }
      setLoadStatus(status)
    }
    
    checkComponents()
  }, [])
  
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#0f172a', 
      color: '#e2e8f0',
      padding: '2rem',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>
        🔍 Component Loading Diagnostic
      </h1>
      
      <div style={{ 
        backgroundColor: '#1e293b', 
        padding: '1.5rem', 
        borderRadius: '8px',
        marginTop: '1rem'
      }}>
        <h2 style={{ marginBottom: '1rem' }}>Component Status:</h2>
        {Object.entries(loadStatus).length === 0 ? (
          <p>Checking components...</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, fontFamily: 'monospace' }}>
            {Object.entries(loadStatus).map(([name, status]) => (
              <li key={name} style={{ 
                padding: '0.5rem', 
                marginBottom: '0.5rem',
                backgroundColor: status.includes('❌') ? '#7f1d1d' : '#14532d',
                borderRadius: '4px'
              }}>
                <strong>{name}:</strong> {status}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#1e293b', borderRadius: '8px' }}>
        <h3>Next Steps:</h3>
        <ol style={{ marginLeft: '1.5rem' }}>
          <li>Check which components show ❌ errors above</li>
          <li>Open browser Console (F12) for detailed error messages</li>
          <li>Share the error details so I can fix them</li>
        </ol>
      </div>
    </div>
  )
}

export default DebugApp

// Made with Bob
