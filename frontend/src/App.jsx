import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ChatRAG from './pages/ChatRAG'
import CodePorter from './pages/CodePorter'
import QADashboard from './pages/QADashboard'
import TriageDashboard from './pages/TriageDashboard'
import CICDMonitor from './pages/CICDMonitor'
import DatasetCleaner from './pages/DatasetCleaner'
import ModelSuggester from './pages/ModelSuggester'
import SchemaOptimizer from './pages/SchemaOptimizer'
import VoiceAssistant from './pages/VoiceAssistant'
import DocTestPipeline from './pages/DocTestPipeline'
import IncidentDebugger from './pages/IncidentDebugger'
import ReviewCoach from './pages/ReviewCoach'
import CodeExplainer from './pages/CodeExplainer'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/rag" replace />} />
        <Route path="rag" element={<ChatRAG />} />
        <Route path="porter" element={<CodePorter />} />
        <Route path="qa" element={<QADashboard />} />
        <Route path="triage" element={<TriageDashboard />} />
        <Route path="cicd" element={<CICDMonitor />} />
        <Route path="cleaner" element={<DatasetCleaner />} />
        <Route path="suggester" element={<ModelSuggester />} />
        <Route path="schema" element={<SchemaOptimizer />} />
        <Route path="voice" element={<VoiceAssistant />} />
        <Route path="doc-test" element={<DocTestPipeline />} />
        <Route path="incident" element={<IncidentDebugger />} />
        <Route path="review" element={<ReviewCoach />} />
        <Route path="explainer" element={<CodeExplainer />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <AppRoutes />
  )
}

export default App

// Made with Bob
