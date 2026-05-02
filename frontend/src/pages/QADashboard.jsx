import { useState } from 'react'
import { TestTube, Play, Loader2, Download, CheckCircle } from 'lucide-react'
import Editor from '@monaco-editor/react'
import axios from 'axios'

export default function QADashboard() {
  const [sourceCode, setSourceCode] = useState('')
  const [language, setLanguage] = useState('javascript')
  const [isGenerating, setIsGenerating] = useState(false)
  const [result, setResult] = useState(null)
  const [selectedTest, setSelectedTest] = useState(0)

  const handleGenerate = async () => {
    if (!sourceCode.trim()) {
      alert('Please enter source code to generate tests')
      return
    }

    setIsGenerating(true)
    setResult(null)

    try {
      const response = await axios.post('/api/qa/generate', {
        code_path: sourceCode,  // Sending code directly for demo
        language: language
      })

      setResult(response.data)
      setSelectedTest(0)
    } catch (error) {
      console.error('Error generating tests:', error)
      alert('Failed to generate tests: ' + (error.response?.data?.detail || error.message))
    } finally {
      setIsGenerating(false)
    }
  }

  const loadDemoCode = () => {
    const demoCode = `// Payment Service
class PaymentService {
  constructor(database, logger) {
    this.db = database;
    this.logger = logger;
  }

  async processPayment(userId, amount, currency, paymentMethod) {
    this.logger.info(\`Processing payment for user: \${userId}\`);
    
    if (amount <= 0) {
      throw new Error('Invalid amount');
    }
    
    const user = await this.db.findUser(userId);
    if (!user) {
      throw new Error('User not found');
    }
    
    const transactionId = this.generateTransactionId();
    const result = await this.chargePaymentMethod(paymentMethod, amount, currency);
    
    if (result.success) {
      await this.db.saveTransaction({
        userId,
        amount,
        currency,
        transactionId,
        status: 'completed'
      });
      
      return { success: true, transactionId };
    }
    
    throw new Error('Payment failed');
  }

  async getPaymentHistory(userId, limit = 10) {
    this.logger.info(\`Fetching payment history for user: \${userId}\`);
    const transactions = await this.db.getTransactions(userId, limit);
    return { userId, transactions };
  }

  async refundPayment(transactionId, amount = null) {
    const transaction = await this.db.getTransaction(transactionId);
    
    if (!transaction) {
      throw new Error('Transaction not found');
    }
    
    const refundAmount = amount || transaction.amount;
    const result = await this.processRefund(transaction.paymentMethod, refundAmount);
    
    if (result.success) {
      await this.db.updateTransaction(transactionId, {
        status: 'refunded',
        refundAmount
      });
      
      return { success: true, refundAmount };
    }
    
    throw new Error('Refund failed');
  }

  generateTransactionId() {
    return \`TXN_\${Date.now()}_\${Math.floor(Math.random() * 10000)}\`;
  }

  async chargePaymentMethod(method, amount, currency) {
    // Simulate payment gateway call
    return { success: true, gatewayResponse: 'approved' };
  }

  async processRefund(method, amount) {
    // Simulate refund gateway call
    return { success: true, gatewayResponse: 'refund_approved' };
  }
}

module.exports = PaymentService;`

    setSourceCode(demoCode)
    setLanguage('javascript')
  }

  const downloadTests = () => {
    if (!result) return

    result.test_files.forEach(testFile => {
      const blob = new Blob([testFile.content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = testFile.filename
      a.click()
      URL.revokeObjectURL(url)
    })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-beige-200 border-b border-beige-300 p-6">
        <h1 className="text-2xl font-bold mb-2">Autonomous QA Engineering Agent</h1>
        <p className="text-black">
          Auto-generate unit tests, integration tests, and coverage reports using CodeLlama
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Source Code */}
        <div className="w-1/2 border-r border-beige-300 flex flex-col">
          <div className="bg-beige-200 border-b border-beige-300 p-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h2 className="font-semibold">Source Code</h2>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-beige-100 border border-beige-300 rounded px-3 py-1 text-sm"
              >
                <option value="javascript">JavaScript</option>
                <option value="python">Python</option>
                <option value="php">PHP</option>
              </select>
            </div>
            <div className="flex gap-2">
              <button
                onClick={loadDemoCode}
                className="flex items-center gap-2 px-3 py-1 bg-beige-100 border border-beige-300 rounded hover:bg-beige-200 text-sm"
              >
                <TestTube className="w-4 h-4" />
                Load Demo
              </button>
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !sourceCode.trim()}
                className="flex items-center gap-2 px-4 py-1 bg-green-600 hover:bg-green-700 disabled:bg-beige-400 disabled:cursor-not-allowed rounded text-sm"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Generate Tests
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="flex-1">
            <Editor
              height="100%"
              language={language}
              value={sourceCode}
              onChange={(value) => setSourceCode(value || '')}
              theme="light"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
              }}
            />
          </div>
        </div>

        {/* Right Panel - Generated Tests */}
        <div className="w-1/2 flex flex-col">
          {!result ? (
            <div className="flex-1 flex items-center justify-center text-black">
              <div className="text-center">
                <TestTube className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg mb-2">No tests generated yet</p>
                <p className="text-sm">
                  Enter source code and click "Generate Tests"
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* Coverage Summary */}
              <div className="bg-beige-200 border-b border-beige-300 p-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-semibold">Test Results</h2>
                  <button
                    onClick={downloadTests}
                    className="flex items-center gap-2 px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
                  >
                    <Download className="w-4 h-4" />
                    Download All
                  </button>
                </div>

                {/* Coverage Metrics */}
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="bg-beige-100 rounded-lg p-3">
                    <div className="text-2xl font-bold text-green-400">
                      {result.coverage.total_coverage.toFixed(1)}%
                    </div>
                    <div className="text-xs text-black">Total Coverage</div>
                  </div>
                  <div className="bg-beige-100 rounded-lg p-3">
                    <div className="text-2xl font-bold text-green-400">
                      {result.tests_generated}
                    </div>
                    <div className="text-xs text-black">Tests Generated</div>
                  </div>
                  <div className="bg-beige-100 rounded-lg p-3">
                    <div className="text-2xl font-bold text-purple-400">
                      {result.test_files.length}
                    </div>
                    <div className="text-xs text-black">Test Files</div>
                  </div>
                </div>

                {/* Test File Selector */}
                <div className="flex gap-2 overflow-x-auto">
                  {result.test_files.map((testFile, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedTest(idx)}
                      className={`px-4 py-2 rounded whitespace-nowrap flex items-center gap-2 ${
                        selectedTest === idx
                          ? 'bg-green-600 text-white'
                          : 'bg-beige-100 text-black hover:bg-beige-400'
                      }`}
                    >
                      <CheckCircle className="w-4 h-4" />
                      {testFile.filename}
                    </button>
                  ))}
                </div>
              </div>

              {/* Test Code */}
              <div className="flex-1 flex flex-col">
                <div className="bg-beige-200 border-b border-beige-300 px-4 py-2 flex items-center justify-between">
                  <span className="text-sm text-black">
                    Framework: <span className="text-green-400">{result.test_files[selectedTest].framework}</span>
                  </span>
                </div>
                <div className="flex-1">
                  <Editor
                    height="100%"
                    language={language}
                    value={result.test_files[selectedTest].content}
                    theme="light"
                    options={{
                      readOnly: true,
                      minimap: { enabled: false },
                      fontSize: 14,
                    }}
                  />
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// Made with Bob
