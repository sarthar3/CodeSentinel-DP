import { Outlet, NavLink } from 'react-router-dom'
import {
  MessageSquare,
  GitBranch,
  TestTube,
  AlertTriangle,
  Activity,
  Shield,
  Database,
  Eraser,
  BrainCircuit,
  Mic,
  FileText,
  Bug,
  MessageCircle,
  BookOpen
} from 'lucide-react'

const stages = [
  // Core Features
  { path: '/rag', icon: MessageSquare, label: '🤖 RAG ChatBot', section: 'core' },
  { path: '/explainer', icon: BookOpen, label: 'Code Explainer', section: 'core' },
  { path: '/qa', icon: TestTube, label: 'QA Agent', section: 'core' },
  { path: '/triage', icon: AlertTriangle, label: 'Triage', section: 'core' },
  { path: '/incident', icon: Bug, label: 'Incident Debugger', section: 'core' },
  { path: '/review', icon: MessageCircle, label: 'Review Coach', section: 'core' },
  { path: '/cleaner', icon: Eraser, label: 'Dataset Cleaner', section: 'core' },
  { path: '/schema', icon: Database, label: 'DB Optimizer', section: 'core' },
  { path: '/voice', icon: Mic, label: 'Repo V-Assist', section: 'core' },
  
  // Advanced Features
  { path: '/porter', icon: GitBranch, label: 'Code Porter', section: 'advanced' },
  { path: '/cicd', icon: Activity, label: 'CI/CD Healer', section: 'advanced' },
  { path: '/suggester', icon: BrainCircuit, label: 'Model Suggester', section: 'advanced' },
  { path: '/doc-test', icon: FileText, label: 'Doc & Test Pipeline', section: 'advanced' },
]

export default function Layout() {
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
              <p className="text-xs text-black">Developer Platform</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-4 overflow-y-auto">
          {/* Core Features */}
          <div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-2 px-4">Core Features</h3>
            <div className="space-y-1">
              {stages.filter(s => s.section === 'core').map((stage) => (
                <NavLink
                  key={stage.path}
                  to={stage.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-green-600 text-white'
                        : 'text-black hover:bg-beige-100 hover:text-black'
                    }`
                  }
                >
                  <stage.icon className="w-5 h-5" />
                  <div className="flex-1">
                    <div className="font-medium text-sm">{stage.label}</div>
                  </div>
                </NavLink>
              ))}
            </div>
          </div>

          {/* Advanced Features */}
          <div>
            <h3 className="text-xs font-semibold text-gray-600 uppercase mb-2 px-4">Advanced Features</h3>
            <div className="space-y-1">
              {stages.filter(s => s.section === 'advanced').map((stage) => (
                <NavLink
                  key={stage.path}
                  to={stage.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'text-black hover:bg-beige-100 hover:text-black'
                    }`
                  }
                >
                  <stage.icon className="w-5 h-5" />
                  <div className="flex-1">
                    <div className="font-medium text-sm">{stage.label}</div>
                  </div>
                </NavLink>
              ))}
            </div>
          </div>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-beige-300">
          <div className="text-sm text-black opacity-75">
            CodeSentinel DP © 2026
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}

// Made with Bob
