import { useState } from 'react'
import { AlertTriangle, Send, Loader2, ExternalLink } from 'lucide-react'
import axios from 'axios'

export default function TriageDashboard() {
  const [issueTitle, setIssueTitle] = useState('')
  const [issueBody, setIssueBody] = useState('')
  const [issueNumber, setIssueNumber] = useState(1)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(null)

  const handleAnalyze = async () => {
    if (!issueTitle.trim() || !issueBody.trim()) {
      alert('Please enter both issue title and description')
      return
    }

    setIsAnalyzing(true)
    setResult(null)

    try {
      const response = await axios.post('/api/triage/analyze', {
        issue_title: issueTitle,
        issue_body: issueBody,
        issue_number: issueNumber
      })

      setResult(response.data)
    } catch (error) {
      console.error('Error analyzing issue:', error)
      alert('Failed to analyze issue: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsAnalyzing(false)
    }
  }

  const loadDemoIssue = () => {
    setIssueTitle('Payment service returns 500 error during checkout')
    setIssueBody(`## Description
Users are experiencing 500 errors when trying to complete checkout. This started happening about 2 hours ago and is affecting approximately 30% of checkout attempts.

## Steps to Reproduce
1. Add items to cart
2. Proceed to checkout
3. Enter payment information
4. Click "Complete Purchase"
5. Error 500 is returned

## Expected Behavior
Payment should be processed successfully and order confirmation should be displayed.

## Actual Behavior
Server returns 500 Internal Server Error. Users cannot complete their purchases.

## Additional Context
- Started at approximately 14:00 UTC
- Error rate: ~30% of attempts
- Affects all payment methods
- No recent deployments

## Error Logs
\`\`\`
Error: Connection timeout
  at PaymentService.processPayment (payment.js:45)
  at async POST /api/checkout (routes.js:123)
\`\`\``)
    setIssueNumber(42)
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'P1':
        return 'bg-red-600'
      case 'P2':
        return 'bg-yellow-600'
      case 'P3':
        return 'bg-green-600'
      default:
        return 'bg-gray-600'
    }
  }

  const getSeverityLabel = (severity) => {
    switch (severity) {
      case 'P1':
        return 'Critical'
      case 'P2':
        return 'High'
      case 'P3':
        return 'Medium'
      default:
        return 'Unknown'
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-beige-200 border-b border-beige-300 p-6">
        <h1 className="text-2xl font-bold mb-2">Automated Issue Triage Agent</h1>
        <p className="text-black">
          Analyze GitHub issues, assign severity, and link to similar past incidents using RAG
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Issue Input */}
        <div className="w-1/2 border-r border-beige-300 flex flex-col p-6 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">GitHub Issue</h2>
            <button
              onClick={loadDemoIssue}
              className="px-3 py-1 bg-beige-100 border border-beige-300 rounded hover:bg-beige-200 text-sm"
            >
              Load Demo Issue
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Issue Number</label>
              <input
                type="number"
                value={issueNumber}
                onChange={(e) => setIssueNumber(parseInt(e.target.value) || 1)}
                className="w-full bg-beige-100 border border-beige-300 rounded px-3 py-2"
                placeholder="Issue #"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Issue Title</label>
              <input
                type="text"
                value={issueTitle}
                onChange={(e) => setIssueTitle(e.target.value)}
                className="w-full bg-beige-100 border border-beige-300 rounded px-3 py-2"
                placeholder="Enter issue title..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Issue Description</label>
              <textarea
                value={issueBody}
                onChange={(e) => setIssueBody(e.target.value)}
                rows={15}
                className="w-full bg-beige-100 border border-beige-300 rounded px-3 py-2 font-mono text-sm"
                placeholder="Enter issue description..."
              />
            </div>

            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !issueTitle.trim() || !issueBody.trim()}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-beige-400 disabled:cursor-not-allowed rounded"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Analyze & Triage
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Panel - Triage Results */}
        <div className="w-1/2 flex flex-col">
          {!result ? (
            <div className="flex-1 flex items-center justify-center text-black">
              <div className="text-center">
                <AlertTriangle className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg mb-2">No triage results yet</p>
                <p className="text-sm">
                  Enter an issue and click "Analyze & Triage"
                </p>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Severity Badge */}
              <div>
                <h3 className="text-sm font-medium text-black mb-2">Severity</h3>
                <div className="flex items-center gap-3">
                  <span className={`${getSeverityColor(result.triage.severity)} px-4 py-2 rounded-lg font-bold text-lg`}>
                    {result.triage.severity}
                  </span>
                  <span className="text-lg">{getSeverityLabel(result.triage.severity)}</span>
                </div>
              </div>

              {/* Category */}
              <div>
                <h3 className="text-sm font-medium text-black mb-2">Category</h3>
                <div className="bg-beige-200 border border-beige-300 rounded-lg p-3">
                  <span className="capitalize">{result.triage.category}</span>
                </div>
              </div>

              {/* Root Cause */}
              <div>
                <h3 className="text-sm font-medium text-black mb-2">Root Cause Analysis</h3>
                <div className="bg-beige-200 border border-beige-300 rounded-lg p-4">
                  <p className="text-sm leading-relaxed">{result.triage.root_cause}</p>
                </div>
              </div>

              {/* Recommended Action */}
              <div>
                <h3 className="text-sm font-medium text-black mb-2">Recommended Action</h3>
                <div className="bg-beige-200 border border-beige-300 rounded-lg p-4">
                  <p className="text-sm leading-relaxed">{result.triage.recommended_action}</p>
                </div>
              </div>

              {/* Similar Incidents */}
              {result.triage.similar_incidents && result.triage.similar_incidents.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-black mb-2">
                    Similar Past Incidents ({result.triage.similar_incidents.length})
                  </h3>
                  <div className="space-y-3">
                    {result.triage.similar_incidents.map((incident, idx) => (
                      <div
                        key={idx}
                        className="bg-beige-200 border border-beige-300 rounded-lg p-4"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <ExternalLink className="w-4 h-4 text-green-400" />
                            <span className="font-medium text-green-400">
                              {incident.source}, page {incident.page}
                            </span>
                          </div>
                          <span className="text-xs text-black">
                            {(incident.relevance_score * 100).toFixed(0)}% match
                          </span>
                        </div>
                        <p className="text-sm text-black line-clamp-3">
                          {incident.excerpt}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Reproduction Steps */}
              {result.triage.reproduction_steps && (
                <div>
                  <h3 className="text-sm font-medium text-black mb-2">Reproduction Steps</h3>
                  <div className="bg-beige-200 border border-beige-300 rounded-lg p-4">
                    <pre className="text-sm whitespace-pre-wrap font-mono">
                      {result.triage.reproduction_steps}
                    </pre>
                  </div>
                </div>
              )}

              {/* Comment Status */}
              <div className="bg-green-900/20 border border-green-700 rounded-lg p-4">
                <div className="flex items-center gap-2 text-green-400">
                  <AlertTriangle className="w-5 h-5" />
                  <span className="font-medium">
                    {result.comment_posted ? 'Comment posted to GitHub' : 'Demo Mode - Comment not posted'}
                  </span>
                </div>
                <p className="text-sm text-black mt-2">
                  In production, this triage analysis would be automatically posted as a comment on the GitHub issue.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Made with Bob
