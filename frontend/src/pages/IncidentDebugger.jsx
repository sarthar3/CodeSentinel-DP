import { useState } from 'react'

export default function IncidentDebugger() {
  const [errorLogs, setErrorLogs] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('analysis')

  const analyzeIncident = async () => {
    if (!errorLogs.trim()) {
      alert('Please provide error logs')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/incident/full-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          error_logs: errorLogs
        })
      })

      const data = await res.json()
      setAnalysis(data)
      setActiveTab('analysis')
    } catch (error) {
      console.error('Error analyzing incident:', error)
      alert('Error analyzing incident. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-300',
      high: 'bg-orange-100 text-orange-800 border-orange-300',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-blue-100 text-blue-800 border-blue-300'
    }
    return colors[severity?.toLowerCase()] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-beige-300 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          🔍 AI-Powered Incident Debugger
        </h1>
        <p className="text-gray-600 mb-6">
          Analyze production incidents, trace root causes, and get actionable fixes
        </p>

        {/* Input Section */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Error Logs / Stack Trace
          </label>
          <textarea
            value={errorLogs}
            onChange={(e) => setErrorLogs(e.target.value)}
            placeholder="Paste your error logs, stack traces, or incident details here..."
            rows={12}
            className="w-full px-4 py-2 border border-beige-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          />
        </div>

        <button
          onClick={analyzeIncident}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Analyzing...' : 'Analyze Incident'}
        </button>

        {loading && (
          <div className="text-center py-8 mt-6">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="text-sm text-gray-600 mt-4">Analyzing incident and tracing root cause...</p>
          </div>
        )}

        {/* Results */}
        {analysis && !loading && (
          <div className="mt-6 border-t border-beige-300 pt-6">
            {/* Tabs */}
            <div className="flex gap-2 mb-4 overflow-x-auto">
              <button
                onClick={() => setActiveTab('analysis')}
                className={`px-4 py-2 rounded-lg whitespace-nowrap ${
                  activeTab === 'analysis'
                    ? 'bg-blue-600 text-white'
                    : 'bg-beige-100 text-gray-700 hover:bg-beige-200'
                }`}
              >
                Root Cause
              </button>
              <button
                onClick={() => setActiveTab('trace')}
                className={`px-4 py-2 rounded-lg whitespace-nowrap ${
                  activeTab === 'trace'
                    ? 'bg-blue-600 text-white'
                    : 'bg-beige-100 text-gray-700 hover:bg-beige-200'
                }`}
              >
                Execution Flow
              </button>
              <button
                onClick={() => setActiveTab('fixes')}
                className={`px-4 py-2 rounded-lg whitespace-nowrap ${
                  activeTab === 'fixes'
                    ? 'bg-blue-600 text-white'
                    : 'bg-beige-100 text-gray-700 hover:bg-beige-200'
                }`}
              >
                Suggested Fixes
              </button>
              <button
                onClick={() => setActiveTab('report')}
                className={`px-4 py-2 rounded-lg whitespace-nowrap ${
                  activeTab === 'report'
                    ? 'bg-blue-600 text-white'
                    : 'bg-beige-100 text-gray-700 hover:bg-beige-200'
                }`}
              >
                Full Report
              </button>
            </div>

            {/* Tab Content */}
            <div className="bg-beige-50 rounded-lg p-6 border border-beige-300">
              {activeTab === 'analysis' && analysis.analysis && (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Root Cause</h3>
                    <p className="text-gray-700">{analysis.analysis.root_cause}</p>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className={`px-3 py-1 rounded-full border ${getSeverityColor(analysis.analysis.severity)}`}>
                      <span className="text-sm font-medium">
                        {analysis.analysis.severity?.toUpperCase() || 'UNKNOWN'}
                      </span>
                    </div>
                    {analysis.analysis.confidence && (
                      <div className="text-sm text-gray-600">
                        Confidence: {(analysis.analysis.confidence * 100).toFixed(0)}%
                      </div>
                    )}
                  </div>

                  {analysis.analysis.contributing_factors && analysis.analysis.contributing_factors.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Contributing Factors</h4>
                      <ul className="space-y-1 text-sm text-gray-700">
                        {analysis.analysis.contributing_factors.map((factor, idx) => (
                          <li key={idx}>• {factor}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {analysis.analysis.affected_components && analysis.analysis.affected_components.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Affected Components</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.analysis.affected_components.map((comp, idx) => (
                          <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                            {comp}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysis.analysis.immediate_actions && analysis.analysis.immediate_actions.length > 0 && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <h4 className="font-medium text-red-900 mb-2">⚠️ Immediate Actions Required</h4>
                      <ol className="space-y-1 text-sm text-red-800 list-decimal list-inside">
                        {analysis.analysis.immediate_actions.map((action, idx) => (
                          <li key={idx}>{action}</li>
                        ))}
                      </ol>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'trace' && analysis.execution_trace && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Execution Flow Trace</h3>
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-white p-4 rounded border border-beige-200">
                    {analysis.execution_trace.execution_flow}
                  </pre>
                </div>
              )}

              {activeTab === 'fixes' && analysis.suggested_fixes && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900 mb-3">Recommended Fixes</h3>
                  {analysis.suggested_fixes.map((fix, idx) => (
                    <div key={idx} className="bg-white border border-beige-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{idx + 1}. {fix.fix}</h4>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          fix.priority === 'high' ? 'bg-red-100 text-red-800' :
                          fix.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {fix.priority?.toUpperCase()}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-3">
                        <div>
                          <span className="font-medium">Effort:</span> {fix.effort_hours} hours
                        </div>
                        <div>
                          <span className="font-medium">Risk:</span> {fix.risk}
                        </div>
                      </div>
                      {fix.implementation_steps && fix.implementation_steps.length > 0 && (
                        <div>
                          <p className="text-sm font-medium text-gray-700 mb-1">Implementation Steps:</p>
                          <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
                            {fix.implementation_steps.map((step, stepIdx) => (
                              <li key={stepIdx}>{step}</li>
                            ))}
                          </ol>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'report' && analysis.report && (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="font-semibold text-gray-900">Incident Report</h3>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(analysis.report)
                        alert('Report copied to clipboard!')
                      }}
                      className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                    >
                      Copy Report
                    </button>
                  </div>
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-white p-4 rounded border border-beige-200 overflow-x-auto">
                    {analysis.report}
                  </pre>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Example Section */}
      <div className="bg-white rounded-lg shadow-sm border border-beige-300 p-6">
        <h3 className="font-semibold text-gray-900 mb-3">💡 Example Error Log</h3>
        <pre className="text-xs text-gray-600 bg-beige-50 p-3 rounded border border-beige-200 overflow-x-auto">
{`ERROR: Database connection timeout
Traceback (most recent call last):
  File "app.py", line 45, in process_payment
    result = db.execute(query)
  File "database.py", line 120, in execute
    raise TimeoutError("Connection timeout after 30s")
TimeoutError: Connection timeout after 30s

Context: Payment processing failed for order #12345
Time: 2024-01-15 14:30:22 UTC`}
        </pre>
      </div>
    </div>
  )
}

// Made with Bob
