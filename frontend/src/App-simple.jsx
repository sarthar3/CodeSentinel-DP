function App() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#0f172a', 
      color: '#e2e8f0',
      padding: '2rem',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>
        🎉 CodeSentinel is Working!
      </h1>
      <p style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>
        If you can see this, React is rendering correctly.
      </p>
      <div style={{ 
        backgroundColor: '#1e293b', 
        padding: '1rem', 
        borderRadius: '8px',
        marginTop: '2rem'
      }}>
        <h2 style={{ marginBottom: '0.5rem' }}>✅ Status Check:</h2>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li>✅ Frontend Server: Running</li>
          <li>✅ React: Rendering</li>
          <li>✅ Styling: Working</li>
        </ul>
      </div>
      <p style={{ marginTop: '2rem', color: '#94a3b8' }}>
        Next: Check if backend is running at{' '}
        <a 
          href="http://localhost:8000/docs" 
          target="_blank"
          style={{ color: '#60a5fa' }}
        >
          http://localhost:8000/docs
        </a>
      </p>
    </div>
  )
}

export default App

// Made with Bob
