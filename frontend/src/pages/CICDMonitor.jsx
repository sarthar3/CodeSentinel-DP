import { Activity, CheckCircle, XCircle, Clock } from 'lucide-react'

export default function CICDMonitor() {
  // Demo data for CI/CD pipeline
  const demoBuilds = [
    {
      id: 1,
      name: 'Build #142',
      status: 'success',
      duration: '2m 34s',
      timestamp: '2 hours ago',
      branch: 'main'
    },
    {
      id: 2,
      name: 'Build #141',
      status: 'failed',
      duration: '1m 12s',
      timestamp: '4 hours ago',
      branch: 'feature/payment-fix',
      error: 'Missing dependency: express@4.18.2',
      autoFixed: true,
      prUrl: 'https://github.com/example/repo/pull/123'
    },
    {
      id: 3,
      name: 'Build #140',
      status: 'success',
      duration: '2m 45s',
      timestamp: '6 hours ago',
      branch: 'main'
    }
  ]

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'running':
        return <Clock className="w-5 h-5 text-green-500 animate-spin" />
      default:
        return <Activity className="w-5 h-5 text-gray-500" />
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-beige-200 border-b border-beige-300 p-6">
        <h1 className="text-2xl font-bold mb-2">Self-Healing CI/CD Pipeline Agent</h1>
        <p className="text-black">
          Monitor builds, detect failures, auto-generate fixes, and create PRs
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          <div className="bg-green-900/20 border border-green-700 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 text-green-400 mb-2">
              <Activity className="w-5 h-5" />
              <span className="font-medium">Demo Mode</span>
            </div>
            <p className="text-sm text-black">
              This is a demonstration of the CI/CD healing concept. In production, this would:
            </p>
            <ul className="text-sm text-black mt-2 ml-4 list-disc space-y-1">
              <li>Monitor GitHub Actions workflows in real-time</li>
              <li>Parse error logs using LLM when builds fail</li>
              <li>Auto-generate fix patches (scanned by Secret Scanner)</li>
              <li>Create pull requests with [BOT] prefix</li>
              <li>Notify team via Slack/email</li>
            </ul>
          </div>

          <h2 className="text-lg font-semibold mb-4">Recent Builds</h2>

          {demoBuilds.map((build) => (
            <div
              key={build.id}
              className="bg-beige-200 border border-beige-300 rounded-lg p-4"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  {getStatusIcon(build.status)}
                  <div>
                    <h3 className="font-semibold">{build.name}</h3>
                    <p className="text-sm text-black">
                      {build.branch} • {build.timestamp}
                    </p>
                  </div>
                </div>
                <span className="text-sm text-black">{build.duration}</span>
              </div>

              {build.status === 'failed' && (
                <div className="mt-3 space-y-3">
                  <div className="bg-red-900/20 border border-red-700 rounded p-3">
                    <p className="text-sm text-red-400 font-mono">{build.error}</p>
                  </div>

                  {build.autoFixed && (
                    <div className="bg-green-900/20 border border-green-700 rounded p-3">
                      <div className="flex items-center gap-2 text-green-400 mb-2">
                        <CheckCircle className="w-4 h-4" />
                        <span className="font-medium">Auto-Fixed</span>
                      </div>
                      <p className="text-sm text-black mb-2">
                        Patch generated and scanned for secrets. Pull request created:
                      </p>
                      <a
                        href={build.prUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-green-400 hover:text-green-300 underline"
                      >
                        {build.prUrl}
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Made with Bob
