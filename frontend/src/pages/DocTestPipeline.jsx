import { useState } from 'react'

export default function DocTestPipeline() {
  const [code, setCode] = useState('')
  const [filePath, setFilePath] = useState('')
  const [language, setLanguage] = useState('python')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('docs')

  const runFullPipeline = async () => {
    if (!code || !filePath) {
      alert('Please provide both code and file path')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/doc-test/pipeline/full', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          file_path: filePath,
          language
        })
      })

      const data = await res.json()
      setResult(data)
    } catch (error) {
      console.error('Error running pipeline:', error)
      alert('Error running pipeline. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const generateDocs = async () => {
    if (!code || !filePath) {
      alert('Please provide both code and file path')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/doc-test/generate-docs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          file_path: filePath
        })
      })

      const data = await res.json()
      setResult({ documentation: data.documentation, analysis: data.analysis })
      setActiveTab('docs')
    } catch (error) {
      console.error('Error generating docs:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateTests = async () => {
    if (!code || !filePath) {
      alert('Please provide both code and file path')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/doc-test/generate-tests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          file_path: filePath,
          language
        })
      })

      const data = await res.json()
      setResult({ tests: data.tests, coverage: data.coverage, suggestions: data.suggestions })
      setActiveTab('tests')
    } catch (error) {
      console.error('Error generating tests:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-beige-300 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          📚 Documentation & Test Automation Pipeline
        </h1>
        <p className="text-gray-600 mb-6">
          Automatically generate documentation and tests for your code changes
        </p>

        {/* Input Section */}
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              File Path
            </label>
            <input
              type="text"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder="e.g., src/utils/helper.py"
              className="w-full px-4 py-2 border border-beige-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-4 py-2 border border-beige-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="java">Java</option>
              <option value="go">Go</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Code
            </label>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Paste your code here..."
              rows={12}
              className="w-full px-4 py-2 border border-beige-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 mb-6">
          <button
            onClick={runFullPipeline}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Run Full Pipeline
          </button>
          <button
            onClick={generateDocs}
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Generate Docs Only
          </button>
          <button
            onClick={generateTests}
            disabled={loading}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Generate Tests Only
          </button>
        </div>

        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="text-sm text-gray-600 mt-4">Processing your code...</p>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="border-t border-beige-300 pt-6">
            {/* Tabs */}
            <div className="flex gap-2 mb-4">
              {result.documentation && (
                <button
                  onClick={() => setActiveTab('docs')}
                  className={`px-4 py-2 rounded-lg ${
                    activeTab === 'docs'
                      ? 'bg-blue-600 text-white'
                      : 'bg-beige-100 text-gray-700 hover:bg-beige-200'
                  }`}
                >
                  Documentation
                </button>
              )}
              {result.tests && (
                <button
                  onClick={() => setActiveTab('tests')}
                  className={`px-4 py-2 rounded-lg ${
                    activeTab === 'tests'
                      ? 'bg-blue-600 text-white'
                      : 'bg-beige-100 text-gray-700 hover:bg-beige-200'
                  }`}
                >
                  Tests
                </button>
              )}
              {result.analysis && (
                <button
                  onClick={() => setActiveTab('analysis')}
                  className={`px-4 py-2 rounded-lg ${
                    activeTab === 'analysis'
                      ? 'bg-blue-600 text-white'
                      : 'bg-beige-100 text-gray-700 hover:bg-beige-200'
                  }`}
                >
                  Analysis
                </button>
              )}
            </div>

            {/* Tab Content */}
            <div className="bg-beige-50 rounded-lg p-4 border border-beige-300">
              {activeTab === 'docs' && result.documentation && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Generated Documentation</h3>
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-white p-4 rounded border border-beige-200">
                    {result.documentation}
                  </pre>
                </div>
              )}

              {activeTab === 'tests' && result.tests && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Generated Tests</h3>
                  {result.coverage && (
                    <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
                      <p className="text-sm font-medium text-gray-900">
                        Estimated Coverage: {result.coverage.estimated_coverage}%
                      </p>
                      <p className="text-xs text-gray-600">
                        {result.coverage.test_functions} test functions, {result.coverage.test_assertions} assertions
                      </p>
                    </div>
                  )}
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-white p-4 rounded border border-beige-200 overflow-x-auto">
                    {result.tests}
                  </pre>
                  {result.suggestions && result.suggestions.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-medium text-gray-900 mb-2">Additional Test Suggestions:</h4>
                      <ul className="space-y-1 text-sm text-gray-700">
                        {result.suggestions.map((suggestion, idx) => (
                          <li key={idx}>• {suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'analysis' && result.analysis && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Change Analysis</h3>
                  <div className="space-y-2 text-sm">
                    <p><strong>Change Type:</strong> {result.analysis.change_type}</p>
                    <p><strong>Documentation Style:</strong> {result.analysis.doc_style}</p>
                    <p><strong>Summary:</strong> {result.analysis.summary}</p>
                    {result.analysis.components && result.analysis.components.length > 0 && (
                      <p><strong>Affected Components:</strong> {result.analysis.components.join(', ')}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Made with Bob
