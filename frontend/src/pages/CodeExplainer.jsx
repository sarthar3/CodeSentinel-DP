import { useState } from 'react'

export default function CodeExplainer() {
  const [code, setCode] = useState('')
  const [audience, setAudience] = useState('business')
  const [detailLevel, setDetailLevel] = useState('summary')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const explainCode = async () => {
    if (!code.trim()) {
      alert('Please provide code to explain')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/explainer/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          audience,
          detail_level: detailLevel
        })
      })

      const data = await res.json()
      setResult(data)
    } catch (error) {
      console.error('Error explaining code:', error)
      alert('Error explaining code. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const audiences = [
    { id: 'business', name: 'Business Stakeholders', icon: '💼' },
    { id: 'executive', name: 'Executive Leadership', icon: '👔' },
    { id: 'technical', name: 'Technical Team', icon: '👨‍💻' },
    { id: 'general', name: 'General Audience', icon: '👥' }
  ]

  const detailLevels = [
    { id: 'summary', name: 'Summary', description: 'Brief overview' },
    { id: 'detailed', name: 'Detailed', description: 'Comprehensive explanation' },
    { id: 'deep-dive', name: 'Deep Dive', description: 'In-depth analysis' }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-beige-300 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          📖 Accessible Code Explainer
        </h1>
        <p className="text-gray-600 mb-6">
          Translate technical code into clear explanations for any audience
        </p>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Target Audience
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {audiences.map((aud) => (
              <button
                key={aud.id}
                onClick={() => setAudience(aud.id)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  audience === aud.id
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-beige-300 bg-white hover:border-blue-300'
                }`}
              >
                <div className="text-2xl mb-2">{aud.icon}</div>
                <div className="text-sm font-medium text-gray-900">{aud.name}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Detail Level
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {detailLevels.map((level) => (
              <button
                key={level.id}
                onClick={() => setDetailLevel(level.id)}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  detailLevel === level.id
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-beige-300 bg-white hover:border-blue-300'
                }`}
              >
                <div className="font-medium text-gray-900 mb-1">{level.name}</div>
                <div className="text-xs text-gray-600">{level.description}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Code to Explain
          </label>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here..."
            rows={12}
            className="w-full px-4 py-2 border border-beige-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          />
        </div>

        <button
          onClick={explainCode}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Explaining...' : 'Explain Code'}
        </button>

        {loading && (
          <div className="text-center py-8 mt-6">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="text-sm text-gray-600 mt-4">Generating explanation...</p>
          </div>
        )}

        {result && !loading && (
          <div className="mt-6 border-t border-beige-300 pt-6">
            <div className="bg-beige-50 rounded-lg p-6 border border-beige-300">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Explanation</h3>
                <div className="flex gap-2 text-xs">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                    {audience}
                  </span>
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded">
                    {detailLevel}
                  </span>
                </div>
              </div>
              
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{result.explanation}</p>
              </div>

              {result.key_concepts && result.key_concepts.length > 0 && (
                <div className="mt-4 pt-4 border-t border-beige-200">
                  <h4 className="font-medium text-gray-900 mb-2">Key Concepts</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.key_concepts.map((concept, idx) => (
                      <span key={idx} className="px-3 py-1 bg-white border border-beige-300 rounded-full text-sm text-gray-700">
                        {concept}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-beige-300 p-6">
        <h3 className="font-semibold text-gray-900 mb-3">💡 Example Use Cases</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>• Explain complex algorithms to product managers</li>
          <li>• Create executive summaries of technical changes</li>
          <li>• Generate user-friendly error messages</li>
          <li>• Document code for non-technical stakeholders</li>
        </ul>
      </div>
    </div>
  )
}

// Made with Bob
