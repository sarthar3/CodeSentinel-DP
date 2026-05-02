import { useState, useRef } from 'react'

export default function VoiceAssistant() {
  const [isRecording, setIsRecording] = useState(false)
  const [transcription, setTranscription] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [repoPath, setRepoPath] = useState('')
  const [repoAnalysis, setRepoAnalysis] = useState(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        await processAudio(audioBlob)
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error accessing microphone:', error)
      alert('Could not access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
      setIsRecording(false)
    }
  }

  const processAudio = async (audioBlob) => {
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.wav')
      if (repoPath) {
        formData.append('repo_path', repoPath)
      }

      const res = await fetch('http://localhost:8000/api/voice/voice-conversation', {
        method: 'POST',
        body: formData
      })

      const data = await res.json()
      setTranscription(data.transcription)
      setResponse(data.response_text)
    } catch (error) {
      console.error('Error processing audio:', error)
      setResponse('Error processing your request. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const analyzeRepository = async () => {
    if (!repoPath) return
    
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/voice/analyze-repository', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: repoPath })
      })

      const data = await res.json()
      setRepoAnalysis(data)
    } catch (error) {
      console.error('Error analyzing repository:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-beige-300 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          🎤 Repo V-Assist (Voice-Driven Assistant)
        </h1>
        <p className="text-gray-600 mb-6">
          Hands-free code review and repository onboarding. Ask questions about your codebase using voice commands.
        </p>

        {/* Repository Path */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Repository Path
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              placeholder="e.g., /path/to/your/repo"
              className="flex-1 px-4 py-2 border border-beige-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={analyzeRepository}
              disabled={!repoPath || loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Analyze
            </button>
          </div>
        </div>

        {/* Repository Analysis */}
        {repoAnalysis && (
          <div className="mb-6 p-4 bg-beige-50 rounded-lg border border-beige-300">
            <h3 className="font-semibold text-gray-900 mb-2">Repository Overview</h3>
            <p className="text-sm text-gray-700 mb-2">{repoAnalysis.architecture}</p>
            <div className="text-sm text-gray-600">
              <p><strong>Files:</strong> {repoAnalysis.structure?.file_count || 0}</p>
              <p><strong>Languages:</strong> {repoAnalysis.structure?.languages?.join(', ') || 'N/A'}</p>
            </div>
          </div>
        )}

        {/* Voice Recording */}
        <div className="flex flex-col items-center space-y-4 mb-6">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={loading || !repoPath}
            className={`w-32 h-32 rounded-full flex items-center justify-center text-white text-4xl transition-all ${
              isRecording 
                ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                : 'bg-blue-600 hover:bg-blue-700'
            } disabled:opacity-50 disabled:cursor-not-allowed shadow-lg`}
          >
            {isRecording ? '⏹️' : '🎤'}
          </button>
          <p className="text-sm text-gray-600">
            {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
          </p>
        </div>

        {/* Transcription */}
        {transcription && (
          <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-gray-900 mb-2">You said:</h3>
            <p className="text-gray-700">{transcription}</p>
          </div>
        )}

        {/* Response */}
        {response && (
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="font-semibold text-gray-900 mb-2">Response:</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{response}</p>
          </div>
        )}

        {loading && (
          <div className="text-center py-4">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="text-sm text-gray-600 mt-2">Processing...</p>
          </div>
        )}
      </div>

      {/* Quick Tips */}
      <div className="bg-white rounded-lg shadow-sm border border-beige-300 p-6">
        <h3 className="font-semibold text-gray-900 mb-3">💡 Quick Tips</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>• Ask "What does this repository do?"</li>
          <li>• Say "Explain the main entry point"</li>
          <li>• Request "How do I get started with this codebase?"</li>
          <li>• Query "What are the key dependencies?"</li>
        </ul>
      </div>
    </div>
  )
}

// Made with Bob
