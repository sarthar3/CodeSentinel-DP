import { useState } from 'react'
import { Activity, CheckCircle, XCircle, Clock, Send, ShieldCheck, ShieldAlert, Terminal, Code } from 'lucide-react'
import axios from 'axios'

export default function CICDMonitor() {
  const [log, setLog] = useState('')
  const [isHealing, setIsHealing] = useState(false)
  const [result, setResult] = useState(null)
  const [step, setStep] = useState(0) // 0: Idle, 1: Analyzing, 2: Patching, 3: Scanning, 4: Done

  const sampleFailure = `
  [INFO] Running build for CodeSentinel v1.0.0
  [INFO] Checking dependencies...
  [ERROR] Failed to compile.
  [ERROR] src/auth/service.js: Line 45:32: 'bcrypt' is not defined  no-undef
  [ERROR] Module not found: Error: Can't resolve 'bcrypt' in 'E:\\project\\src\\auth'
  [INFO] Build failed with exit code 1
  `

  const handleHeal = async () => {
    if (!log.trim()) return

    setIsHealing(true)
    setResult(null)
    setStep(1)

    try {
      // Simulate steps for better UX
      setTimeout(() => setStep(2), 1500)
      setTimeout(() => setStep(3), 3000)

      const response = await axios.post('/api/cicd/heal', { log })
      
      setTimeout(() => {
        setResult(response.data)
        setStep(4)
        setIsHealing(false)
      }, 4500)

    } catch (error) {
      console.error('Healing failed:', error)
      alert('Healing process failed. Check console for details.')
      setIsHealing(false)
      setStep(0)
    }
  }

  const loadSample = () => setLog(sampleFailure)

  return (
    <div className="flex flex-col h-full bg-beige-100">
      {/* Header */}
      <div className="bg-beige-200 border-b border-beige-300 p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold mb-2">Self-Healing CI/CD Pipeline Agent</h1>
            <p className="text-black/70">
              Paste failing build logs to auto-generate patches and verify security.
            </p>
          </div>
          <button 
            onClick={loadSample}
            className="px-4 py-2 bg-beige-100 border border-beige-300 rounded hover:bg-beige-200 text-sm font-medium"
          >
            Try Sample Failure
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Left: Input */}
          <div className="space-y-4">
            <div className="bg-beige-200 border border-beige-300 rounded-lg overflow-hidden flex flex-col h-[500px]">
              <div className="bg-beige-300 px-4 py-2 border-b border-beige-300 flex items-center gap-2">
                <Terminal className="w-4 h-4" />
                <span className="text-sm font-semibold uppercase tracking-wider">Build Logs</span>
              </div>
              <textarea
                value={log}
                onChange={(e) => setLog(e.target.value)}
                placeholder="Paste failing CI/CD logs here..."
                className="flex-1 p-4 bg-black/90 text-green-400 font-mono text-sm resize-none focus:outline-none"
              />
              <button
                onClick={handleHeal}
                disabled={isHealing || !log.trim()}
                className="p-4 bg-green-600 hover:bg-green-700 disabled:bg-beige-400 disabled:cursor-not-allowed text-white font-bold transition-colors flex items-center justify-center gap-2"
              >
                {isHealing ? <Clock className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                {isHealing ? 'Healing in Progress...' : 'Heal Build Failure'}
              </button>
            </div>
          </div>

          {/* Right: Results */}
          <div className="space-y-4">
            {!result && !isHealing && (
              <div className="h-full border-2 border-dashed border-beige-300 rounded-lg flex flex-col items-center justify-center p-8 text-center bg-beige-200/50">
                <Activity className="w-12 h-12 text-beige-400 mb-4" />
                <h3 className="text-lg font-semibold text-black/40">Ready to Heal</h3>
                <p className="text-sm text-black/30 max-w-xs">
                  Provide a failing build log to begin the automated recovery process.
                </p>
              </div>
            )}

            {isHealing && (
              <div className="bg-beige-200 border border-beige-300 rounded-lg p-6 space-y-6">
                <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 animate-spin" />
                  Healing Pipeline
                </h3>
                <div className="space-y-4">
                  {[
                    { s: 1, label: 'Analyzing Build Logs', desc: 'Identifying root cause and error patterns' },
                    { s: 2, label: 'Generating Fix Patch', desc: 'Constructing code-level resolution' },
                    { s: 3, label: 'Secret Scanning', desc: 'Verifying patch security integrity' }
                  ].map((item) => (
                    <div key={item.s} className={`flex items-start gap-4 transition-opacity duration-500 ${step < item.s ? 'opacity-20' : 'opacity-100'}`}>
                      <div className={`mt-1 rounded-full p-1 ${step > item.s ? 'bg-green-600 text-white' : 'bg-green-600/20 text-green-600'}`}>
                        {step > item.s ? <CheckCircle className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
                      </div>
                      <div>
                        <p className="font-bold text-sm">{item.label}</p>
                        <p className="text-xs text-black/60">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result && (
              <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {/* Analysis Card */}
                <div className="bg-beige-200 border border-beige-300 rounded-lg overflow-hidden">
                  <div className="bg-red-600 px-4 py-2 text-white flex items-center justify-between">
                    <span className="text-xs font-bold uppercase">Incident Detected</span>
                    <span className="text-xs">{result.analysis.error_type}</span>
                  </div>
                  <div className="p-4 bg-red-50">
                    <p className="text-sm font-bold text-red-900 mb-1">{result.analysis.error_message}</p>
                    <p className="text-xs text-red-700">{result.analysis.root_cause}</p>
                  </div>
                </div>

                {/* Security Card */}
                <div className={`bg-beige-200 border border-beige-300 rounded-lg p-4 flex items-center gap-4 ${result.safety.is_safe ? 'bg-green-50' : 'bg-orange-50'}`}>
                  {result.safety.is_safe ? (
                    <ShieldCheck className="w-8 h-8 text-green-600" />
                  ) : (
                    <ShieldAlert className="w-8 h-8 text-orange-600" />
                  )}
                  <div>
                    <h4 className={`font-bold ${result.safety.is_safe ? 'text-green-900' : 'text-orange-900'}`}>
                      {result.safety.is_safe ? 'Patch Verified Safe' : 'Security Warning'}
                    </h4>
                    <p className="text-xs text-black/60">
                      {result.safety.is_safe 
                        ? 'No secrets or sensitive data detected in the suggested fix.' 
                        : `Found ${result.safety.findings_count} potential security issue(s).`}
                    </p>
                  </div>
                </div>

                {/* Patch Card */}
                <div className="bg-beige-200 border border-beige-300 rounded-lg overflow-hidden">
                  <div className="bg-beige-300 px-4 py-2 border-b border-beige-300 flex items-center gap-2">
                    <Code className="w-4 h-4" />
                    <span className="text-sm font-semibold">Suggested Fix</span>
                  </div>
                  <div className="p-4 bg-black/90 text-white font-mono text-sm overflow-x-auto whitespace-pre">
                    {result.patch.suggested_fix}
                  </div>
                  <div className="p-4 bg-beige-200 border-t border-beige-300">
                    <p className="text-xs text-black/70 italic">
                      " {result.patch.explanation} "
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Made with Bob
