import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, MessageSquare, Mic, MicOff, Volume2 } from 'lucide-react'
import axios from 'axios'

export default function ChatRAG() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [interimTranscript, setInterimTranscript] = useState('')
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [useTransformer, setUseTransformer] = useState(false)
  const [transformerAvailable, setTransformerAvailable] = useState(false)
  const messagesEndRef = useRef(null)
  const recognitionRef = useRef(null)
  const silenceTimerRef = useRef(null)

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognition = new SpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'en-US'

      recognition.onresult = (event) => {
        clearTimeout(silenceTimerRef.current)
        let interim = ''
        let final = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            final += transcript
          } else {
            interim += transcript
          }
        }

        const fullTranscript = (final + interim).trim()
        setInterimTranscript(fullTranscript)

        // Auto-send after 2 seconds of silence
        if (fullTranscript) {
          silenceTimerRef.current = setTimeout(() => {
            if (fullTranscript) {
              recognition.stop()
              setQuery(fullTranscript)
              setInterimTranscript('')
              // Auto-submit
              handleVoiceSubmit(fullTranscript)
            }
          }, 2000)
        }
      }

      recognition.onend = () => {
        setIsListening(false)
        setInterimTranscript('')
      }

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        setInterimTranscript('')
      }

      recognitionRef.current = recognition
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const speakText = (text) => {
    if (!voiceEnabled || !window.speechSynthesis) return
    
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 1.1
    utterance.pitch = 1
    utterance.volume = 1
    
    const voices = window.speechSynthesis.getVoices()
    const englishVoice = voices.find(v => v.lang.includes('en'))
    if (englishVoice) {
      utterance.voice = englishVoice
    }
    
    window.speechSynthesis.speak(utterance)
  }

  // Stop speech when voice is toggled off
  useEffect(() => {
    if (!voiceEnabled && window.speechSynthesis) {
      window.speechSynthesis.cancel()
    }
  }, [voiceEnabled])

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.')
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
      setInterimTranscript('')
    } else {
      setIsListening(true)
      recognitionRef.current.start()
    }
  }

  const handleVoiceSubmit = async (text) => {
    if (!text.trim() || isLoading) return
    
    const userQuery = text.trim()
    setQuery('')
    setIsLoading(true)

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: userQuery,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])

    // Create assistant message placeholder
    const assistantMessage = {
      id: Date.now() + 1,
      type: 'assistant',
      content: '',
      sources: [],
      status: 'loading',
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, assistantMessage])

    try {
      const eventSource = new EventSource(
        `http://localhost:8000/api/rag/query/stream?query=${encodeURIComponent(userQuery)}&top_k=3&use_transformer=${useTransformer}`
      )

      let currentContent = ''
      let sources = []

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === 'status') {
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, status: data.message }
                : msg
            ))
          } else if (data.type === 'sources') {
            sources = data.data
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, sources: data.data }
                : msg
            ))
          } else if (data.type === 'token') {
            currentContent += data.data
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, content: currentContent, status: 'streaming' }
                : msg
            ))
          } else if (data.type === 'answer') {
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, content: data.data, status: 'complete' }
                : msg
            ))
          } else if (data.type === 'done') {
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, status: 'complete' }
                : msg
            ))
            eventSource.close()
            setIsLoading(false)
            
            // Speak the response
            if (currentContent) {
              speakText(currentContent)
            }
            
            axios.post('http://localhost:8000/api/history', {
              query: userQuery,
              answer: currentContent
            }).catch(err => console.error("Failed to save history", err))
          } else if (data.type === 'error') {
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, content: `Error: ${data.message}`, status: 'error' }
                : msg
            ))
            eventSource.close()
            setIsLoading(false)
          }
        } catch (err) {
          console.error('Error parsing SSE data:', err)
        }
      }

      eventSource.onerror = (error) => {
        console.error('SSE error:', error)
        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessage.id
            ? { ...msg, content: 'Connection error. Please try again.', status: 'error' }
            : msg
        ))
        eventSource.close()
        setIsLoading(false)
      }

    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => prev.map(msg =>
        msg.id === assistantMessage.id
          ? { ...msg, content: 'Failed to query RAG system.', status: 'error' }
          : msg
      ))
      setIsLoading(false)
    }
  }

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/history');
        const historyMessages = [];
        response.data.forEach(item => {
          historyMessages.push({
            id: `user-${item.id}`,
            type: 'user',
            content: item.query,
            timestamp: item.created_at
          });
          historyMessages.push({
            id: `assistant-${item.id}`,
            type: 'assistant',
            content: item.answer,
            status: 'complete',
            timestamp: item.created_at
          });
        });
        setMessages(historyMessages);
      } catch (error) {
        console.error('Failed to load history', error);
      }
    };
    
    const checkTransformerAvailability = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/rag/health');
        setTransformerAvailable(response.data.transformer_available || false);
      } catch (error) {
        console.error('Failed to check transformer availability', error);
      }
    };
    
    loadHistory();
    checkTransformerAvailability();
  }, []);

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim() || isLoading) return

    const userQuery = query.trim()
    setQuery('')
    setIsLoading(true)

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: userQuery,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])

    // Create assistant message placeholder
    const assistantMessage = {
      id: Date.now() + 1,
      type: 'assistant',
      content: '',
      sources: [],
      status: 'loading',
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, assistantMessage])

    try {
      // Use SSE streaming endpoint
      const eventSource = new EventSource(
        `http://localhost:8000/api/rag/query/stream?query=${encodeURIComponent(userQuery)}&top_k=3&use_transformer=${useTransformer}`
      )

      let currentContent = ''
      let sources = []

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === 'status') {
            // Update status message
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, status: data.message }
                : msg
            ))
          } else if (data.type === 'sources') {
            // Store sources
            sources = data.data
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, sources: data.data }
                : msg
            ))
          } else if (data.type === 'token') {
            // Append token to content
            currentContent += data.data
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, content: currentContent, status: 'streaming' }
                : msg
            ))
          } else if (data.type === 'answer') {
            // Complete answer (non-streaming fallback)
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, content: data.data, status: 'complete' }
                : msg
            ))
          } else if (data.type === 'done') {
            // Streaming complete
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, status: 'complete' }
                : msg
            ))
            eventSource.close()
            setIsLoading(false)
            
            // Speak the response
            if (currentContent) {
              speakText(currentContent)
            }
            
            // Save to DB
            axios.post('http://localhost:8000/api/history', {
              query: userQuery,
              answer: currentContent
            }).catch(err => console.error("Failed to save history", err));
          } else if (data.type === 'error') {
            // Error occurred
            setMessages(prev => prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, content: `Error: ${data.message}`, status: 'error' }
                : msg
            ))
            eventSource.close()
            setIsLoading(false)
          }
        } catch (err) {
          console.error('Error parsing SSE data:', err)
        }
      }

      eventSource.onerror = (error) => {
        console.error('SSE error:', error)
        setMessages(prev => prev.map(msg =>
          msg.id === assistantMessage.id
            ? { ...msg, content: 'Connection error. Please try again.', status: 'error' }
            : msg
        ))
        eventSource.close()
        setIsLoading(false)
      }

    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => prev.map(msg =>
        msg.id === assistantMessage.id
          ? { ...msg, content: 'Failed to query RAG system.', status: 'error' }
          : msg
      ))
      setIsLoading(false)
    }
  }

  const toggleSources = (messageId) => {
    setExpandedSources(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }))
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-beige-200 border-b border-beige-300 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">RAG ChatBot</h1>
            <p className="text-black">
              Voice-enabled AI assistant with RAG knowledge base and general Q&A
            </p>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                {useTransformer ? '🧠 DialoGPT + BERT' : '🚀 Groq Llama 3.3'}
              </span>
              {transformerAvailable && (
                <span className="text-xs text-green-600">✓ Transformers Ready</span>
              )}
            </div>
          </div>
          <div className="flex gap-3">
            {transformerAvailable && (
              <button
                onClick={() => setUseTransformer(!useTransformer)}
                className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                  useTransformer
                    ? 'bg-purple-600 text-white hover:bg-purple-700'
                    : 'bg-gray-400 text-white hover:bg-gray-500'
                }`}
                title={useTransformer ? 'Using DialoGPT + BERT' : 'Using Groq Llama'}
              >
                <span className="text-sm">{useTransformer ? '🧠 Transformer' : '🚀 Groq'}</span>
              </button>
            )}
            <button
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                voiceEnabled
                  ? 'bg-green-600 text-white hover:bg-green-700'
                  : 'bg-gray-400 text-white hover:bg-gray-500'
              }`}
              title={voiceEnabled ? 'Voice responses enabled' : 'Voice responses disabled'}
            >
              <Volume2 className="w-4 h-4" />
              <span className="text-sm">{voiceEnabled ? 'Voice On' : 'Voice Off'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="text-center text-black py-12 flex flex-col items-center justify-center h-full">
            <h2 className="text-4xl font-bold mb-6">Welcome 👋</h2>
            <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-lg mb-2">No messages yet</p>
            <p className="text-sm">
              Try asking: "Have we ever had a database timeout causing payment failure?"
            </p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl rounded-lg p-4 relative ${
                message.type === 'user'
                  ? 'bg-green-600 text-white'
                  : 'bg-beige-200 border border-beige-300'
              }`}
            >
              {message.type === 'user' ? (
                <div className="pr-12">
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              ) : (
                <div className="pr-12">
                  {message.status === 'loading' && (
                    <div className="flex items-center gap-2 text-black">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>{message.status || 'Processing...'}</span>
                    </div>
                  )}
                  
                  {message.content && (
                    <div className="prose max-w-none">
                      <p className="whitespace-pre-wrap text-gray-900">{message.content}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Timestamp */}
              {message.timestamp && (
                <div 
                  className={`absolute bottom-2 right-2 text-[10px] opacity-70 ${
                    message.type === 'user' ? 'text-white' : 'text-gray-500'
                  }`}
                >
                  {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-beige-200 border-t border-beige-300 p-6">
        {interimTranscript && (
          <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800 italic">
              🎤 Listening: "{interimTranscript}"...
            </p>
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type or speak your question..."
            className="flex-1 bg-beige-100 border border-beige-300 rounded-lg px-4 py-3 text-black placeholder-beige-600 focus:outline-none focus:ring-2 focus:ring-green-500"
            disabled={isLoading || isListening}
          />
          <button
            type="button"
            onClick={toggleVoiceInput}
            disabled={isLoading}
            className={`rounded-lg px-5 py-3 flex items-center gap-2 transition-all ${
              isListening
                ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            } disabled:bg-beige-400 disabled:cursor-not-allowed`}
            title={isListening ? 'Stop listening' : 'Start voice input'}
          >
            {isListening ? (
              <>
                <MicOff className="w-5 h-5" />
                <span>Stop</span>
              </>
            ) : (
              <>
                <Mic className="w-5 h-5" />
                <span>Voice</span>
              </>
            )}
          </button>
          <button
            type="submit"
            disabled={isLoading || !query.trim() || isListening}
            className="bg-green-600 hover:bg-green-700 disabled:bg-beige-400 disabled:cursor-not-allowed text-white rounded-lg px-6 py-3 flex items-center gap-2 transition-colors"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Send</span>
              </>
            )}
          </button>
        </form>
        <p className="text-xs text-gray-600 mt-2">
          💡 Tip: Click the microphone and speak naturally. I'll auto-send after 2 seconds of silence.
        </p>
      </div>
    </div>
  )
}

// Made with Bob
