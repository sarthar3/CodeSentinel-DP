import { useState } from 'react'

export default function ReviewCoach() {
  const [comment, setComment] = useState('')
  const [codeDiff, setCodeDiff] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [reviewerStyle, setReviewerStyle] = useState('balanced')
  const [mode, setMode] = useState('improve')

  const analyzeComment = async () => {
    if (!comment.trim()) {
      alert('Please provide a comment to analyze')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/review/analyze-sentiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment })
      })

      const data = await res.json()
      setResult({ sentiment: data })
    } catch (error) {
      console.error('Error analyzing comment:', error)
    } finally {
      setLoading(false)
    }
  }

  const improveComment = async () => {
    if (!comment.trim()) {
      alert('Please provide a comment to improve')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/review/improve-comment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          comment,
          reviewer_style: reviewerStyle
        })
      })

      const data = await res.json()
      setResult(data)
    } catch (error) {
      console.error('Error improving comment:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateReview = async () => {
    if (!codeDiff.trim()) {
      alert('Please provide code diff to review')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/review/generate-review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code_diff: codeDiff
        })
      })

      const data = await res.json()
      setResult({ feedback: data.feedback })
    } catch (error) {
      console.error('Error generating review:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (sentiment) => {
    const colors = {
      positive: 'bg-green-100 text-green-800 border-green-300',
      neutral: 'bg-gray-100 text-gray-800 border-gray-300',
      negative: 'bg-red-100 text-red-800 border-red-300'
    }
    return colors[sentiment] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-beige-300 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          💬 Sentiment-Aware Code Review Coach
        </h1>
        <p className="text-gray-600 mb-6">
          Improve code review comments to be more constructive and generate AI-powered reviews
        </p>

        {/* Mode Selection */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setMode('improve')}
            className={`px-4 py-2 rounded-lg ${
              mode === 'improve'
                ? 'bg-blue-600 text-white'
                : 'bg-beige-100 text-gray-700 hover:bg-beige-200'
            }`}
          >
            Improve Comment
          </button>
          <button
            onClick={() => setMode('generate')}
            className={`px-4 py-2 rounded-lg ${
              mode === 'generate'
                ? 'bg-blue-600 text-white'
                : 'bg-beige-100 text-gray-700 hover:bg-beige-200'
            }`}
          >
            Generate Review
          </button>
        </div>

        {mode === 'improve' ? (
          <div className="space-y-4">
            {/* Reviewer Style */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reviewer Style
              </label>
              <select
                value={reviewerStyle}
                onChange={(e) => setReviewerStyle(e.target.value)}
                className="w-full px-4 py-2 border border-beige-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="gentle">Gentle (Very polite and encouraging)</option>
                <option value="balanced">Balanced (Professional and constructive)</option>
                <option value="direct">Direct (Clear and straightforward)</option>
              </select>
            </div>

            {/* Comment Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review Comment
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Enter your code review comment..."
                rows={6}
                className="w-full px-4 py-2 border border-beige-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={analyzeComment}
                disabled={loading}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Analyze Sentiment
              </button>
              <button
                onClick={improveComment}
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Improve Comment
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Code Diff Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Code Diff
              </label>
              <textarea
                value={codeDiff}
                onChange={(e) => setCodeDiff(e.target.value)}
                placeholder="Paste code diff here..."
                rows={12}
                className="w-full px-4 py-2 border border-beige-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>

            <button
              onClick={generateReview}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Generate Review
            </button>
          </div>
        )}

        {loading && (
          <div className="text-center py-8 mt-6">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="text-sm text-gray-600 mt-4">Processing...</p>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="mt-6 border-t border-beige-300 pt-6">
            {/* Sentiment Analysis */}
            {result.sentiment && (
              <div className="bg-beige-50 rounded-lg p-4 border border-beige-300 mb-4">
                <h3 className="font-semibold text-gray-900 mb-3">Sentiment Analysis</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-700">Overall:</span>
                    <span className={`px-3 py-1 rounded-full border text-sm font-medium ${getSentimentColor(result.sentiment.overall_sentiment)}`}>
                      {result.sentiment.overall_sentiment?.toUpperCase()}
                    </span>
                  </div>
                  
                  {result.sentiment.tones && result.sentiment.tones.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-700">Detected Tones:</span>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {result.sentiment.tones.map((tone, idx) => (
                          <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                            {tone}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Polarity:</span>
                      <span className="ml-2 text-gray-600">{result.sentiment.polarity?.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Subjectivity:</span>
                      <span className="ml-2 text-gray-600">{result.sentiment.subjectivity?.toFixed(2)}</span>
                    </div>
                  </div>

                  {result.sentiment.needs_improvement && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
                      ⚠️ This comment could be improved to be more constructive
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Improved Comment */}
            {result.improved && result.original && (
              <div className="space-y-4">
                <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                  <h3 className="font-semibold text-gray-900 mb-2">Original Comment</h3>
                  <p className="text-gray-700">{result.original}</p>
                </div>

                {result.was_improved && (
                  <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                    <h3 className="font-semibold text-gray-900 mb-2">✨ Improved Comment</h3>
                    <p className="text-gray-700">{result.improved}</p>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(result.improved)
                        alert('Improved comment copied!')
                      }}
                      className="mt-3 px-4 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                    >
                      Copy Improved Comment
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Generated Feedback */}
            {result.feedback && (
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Generated Review Feedback</h3>
                {result.feedback.map((item, idx) => (
                  <div key={idx} className="bg-white border border-beige-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          item.type === 'issue' ? 'bg-red-100 text-red-800' :
                          item.type === 'suggestion' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {item.type?.toUpperCase()}
                        </span>
                        {item.line && (
                          <span className="text-xs text-gray-500">Line {item.line}</span>
                        )}
                      </div>
                      <span className={`px-2 py-1 rounded text-xs ${
                        item.severity === 'high' ? 'bg-red-100 text-red-800' :
                        item.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {item.severity?.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm">{item.comment}</p>
                    {item.sentiment && (
                      <div className="mt-2 text-xs text-gray-500">
                        Sentiment: {item.sentiment.overall_sentiment}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Tips */}
      <div className="bg-white rounded-lg shadow-sm border border-beige-300 p-6">
        <h3 className="font-semibold text-gray-900 mb-3">💡 Tips for Better Code Reviews</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>✓ Be specific and actionable</li>
          <li>✓ Explain the "why" behind suggestions</li>
          <li>✓ Use constructive language</li>
          <li>✓ Acknowledge good practices</li>
          <li>✗ Avoid vague or harsh language</li>
          <li>✗ Don't make it personal</li>
        </ul>
      </div>
    </div>
  )
}

// Made with Bob
