import { useState } from 'react'
import { Shield, MessageSquare, GitBranch, TestTube, AlertTriangle, Activity } from 'lucide-react'
import ChatRAG from './pages/ChatRAG'
import CodePorter from './pages/CodePorter'
import QADashboard from './pages/QADashboard'
import TriageDashboard from './pages/TriageDashboard'
import CICDMonitor from './pages/CICDMonitor'

const stages = [
  { id: 'rag', icon: MessageSquare, label: 'RAG Chat', stage: 'Stage 1', component: ChatRAG },
  { id: 'porter', icon: GitBranch, label: 'Code Porter', stage: 'Stage 2', component: CodePorter },
  { id: 'qa', icon: TestTube, label: 'QA Agent', stage: 'Stage 3', component: QADashboard },
  { id: 'triage', icon: AlertTriangle, label: 'Triage', stage: 'Stage 4', component: TriageDashboard },
  { id: 'cicd', icon: Activity, label: 'CI/CD Healer', stage: 'Stage 5', component: CICDMonitor },
]

function App() {
  const [activeStage, setActiveStage] = useState('rag')
  
  const ActiveComponent = stages.find(s => s.id === activeStage)?.component || ChatRAG

  return (
    <div className="flex h-screen bg-beige-100 text-black">
      {/* Sidebar */}
      <aside className="w-64 bg-beige-200 border-r border-beige-300 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-beige-300">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-green-500" />
            <div>
              <h1 className="text-xl font-bold">CodeSentinel</h1>
              <p className="text-xs text-black">AI Developer Platform</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {stages.map((stage) => (
            <button
              key={stage.id}
              onClick={() => setActiveStage(stage.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                activeStage === stage.id
                  ? 'bg-green-600 text-white'
                  : 'text-black hover:bg-beige-100 hover:text-black'
              }`}
            >
              <stage.icon className="w-5 h-5" />
              <div className="flex-1 text-left">
                <div className="font-medium">{stage.label}</div>
                <div className="text-xs opacity-75">{stage.stage}</div>
              </div>
            </button>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-beige-300">
          <div className="text-xs text-black">
            <div className="font-medium mb-1">Stage 6: Secret Scanner</div>
            <div>CLI Tool (Pre-commit Hook)</div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <ActiveComponent />
      </main>
    </div>
  )
}

export default App

// Made with Bob
