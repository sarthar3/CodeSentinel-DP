import { useState } from 'react'
import { GitBranch, Upload, Loader2, Download, FileCode } from 'lucide-react'
import Editor from '@monaco-editor/react'
import axios from 'axios'

export default function CodePorter() {
  const [sourceCode, setSourceCode] = useState('')
  const [language, setLanguage] = useState('php')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [selectedService, setSelectedService] = useState(0)
  const [activeTab, setActiveTab] = useState('code')

  const handleAnalyze = async () => {
    if (!sourceCode.trim()) {
      alert('Please enter source code to analyze')
      return
    }

    setIsAnalyzing(true)
    setResult(null)

    try {
      const response = await axios.post('/api/porter/analyze', {
        source_code: sourceCode,
        language: language,
        target_language: 'javascript'
      })

      setResult(response.data)
      setSelectedService(0)
    } catch (error) {
      console.error('Error analyzing code:', error)
      const errorDetail = error.response?.data?.detail || error.message;
      alert(`⚠️ Analysis Failed\n\n${errorDetail}`)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const loadDemoCode = () => {
    if (language === 'javascript') {
      setSourceCode(`// Legacy Express.js Monolith - User & Product Management
const express = require('express');
const app = express();
app.use(express.json());

// User Context
const registerUser = (username, email, password) => {
  console.log("Registering user:", username);
  return { id: 1, username, email };
};

const loginUser = (email, password) => {
  console.log("Logging in user:", email);
  return { id: 1, token: "JWT_TOKEN" };
};

// Product Context
const fetchProduct = (id) => {
  return { id, name: "Sample Product", price: 99.99 };
};

const createProduct = (name, price) => {
  return { id: Date.now(), name, price };
};

app.listen(3000, () => console.log('Server running'));`);
    } else if (language === 'python') {
      setSourceCode(`# Legacy Flask Monolith - Order & Shipping Management
from flask import Flask, request, jsonify
app = Flask(__name__)

# Order Context
@app.route('/order/create', methods=['POST'])
def order_create():
    data = request.json
    return jsonify({"order_id": 123, "status": "created"})

@app.route('/order/cancel', methods=['POST'])
def order_cancel():
    order_id = request.json.get('id')
    return jsonify({"order_id": order_id, "status": "cancelled"})

# Shipping Context
@app.route('/shipping/track', methods=['GET'])
def shipping_track():
    track_id = request.args.get('id')
    return jsonify({"track_id": track_id, "status": "in_transit"})

if __name__ == '__main__':
    app.run()`);
    } else {
      // PHP Demo
      setSourceCode(`<?php
/**
 * Legacy PHP Monolith - Payment & Invoice System
 */

class PaymentController {
    public function payment_process($amount, $currency, $card_token) {
        // Logic to process payment
        return ["status" => "success", "transaction_id" => "TXN_" . time()];
    }

    public function payment_refund($transaction_id, $amount) {
        // Logic to refund payment
        return ["status" => "refunded", "amount" => $amount];
    }
}

class InvoiceManager {
    public function invoice_generate($order_id, $user_id) {
        // Logic to generate PDF invoice
        return ["invoice_url" => "https://storage.codesentinel.ai/inv_" . $order_id . ".pdf"];
    }

    public function invoice_send_email($invoice_id, $email) {
        // Logic to send email
        return ["sent" => true];
    }
}
?>`);
    }
  }

  const downloadService = (service) => {
    const files = [
      { name: 'index.js', content: service.code },
      { name: 'Dockerfile', content: service.dockerfile },
      { name: 'openapi.json', content: JSON.stringify(service.openapi_spec, null, 2) },
      { name: 'package.json', content: JSON.stringify({
        name: `${service.name}-service`,
        version: '1.0.0',
        dependencies: {
          express: '^4.18.2',
          cors: '^2.8.5',
          dotenv: '^16.3.1'
        }
      }, null, 2)}
    ]

    files.forEach(file => {
      const blob = new Blob([file.content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${service.name}-${file.name}`
      a.click()
      URL.revokeObjectURL(url)
    })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-beige-200 border-b border-beige-300 p-6">
        <h1 className="text-2xl font-bold mb-2">Legacy Code to Microservices Porter</h1>
        <p className="text-black">
          Analyze legacy monoliths (PHP/JavaScript/Python) and generate modern microservices with Docker + OpenAPI
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Source Code */}
        <div className="w-1/2 border-r border-beige-300 flex flex-col">
          <div className="bg-beige-200 border-b border-beige-300 p-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h2 className="font-semibold">Legacy Code</h2>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-beige-100 border border-beige-300 rounded px-3 py-1 text-sm"
              >
                <option value="php">PHP</option>
                <option value="javascript">JavaScript</option>
                <option value="python">Python</option>
              </select>
            </div>
            <div className="flex gap-2">
              <button
                onClick={loadDemoCode}
                className="flex items-center gap-2 px-3 py-1 bg-beige-100 border border-beige-300 rounded hover:bg-beige-200 text-sm"
              >
                <Upload className="w-4 h-4" />
                Load Demo
              </button>
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing || !sourceCode.trim()}
                className="flex items-center gap-2 px-4 py-1 bg-green-600 hover:bg-green-700 disabled:bg-beige-400 disabled:cursor-not-allowed rounded text-sm"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <GitBranch className="w-4 h-4" />
                    Analyze & Generate
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

        {/* Right Panel - Generated Microservices */}
        <div className="w-1/2 flex flex-col">
          {!result ? (
            <div className="flex-1 flex items-center justify-center text-black">
              <div className="text-center">
                <FileCode className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg mb-2">No microservices generated yet</p>
                <p className="text-sm text-black/60 max-w-xs mx-auto">
                  Paste a legacy monolith (functions/classes) or use <b>"Load Demo"</b> to see the AI identify bounded contexts and generate microservices.
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* Service Selector */}
              <div className="bg-beige-200 border-b border-beige-300 p-4">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="font-semibold">
                    Generated Microservices ({result.microservices.length})
                  </h2>
                  <button
                    onClick={() => downloadService(result.microservices[selectedService])}
                    className="flex items-center gap-2 px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                </div>
                <div className="flex gap-2 overflow-x-auto">
                  {result.microservices.map((service, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedService(idx)}
                      className={`px-4 py-2 rounded whitespace-nowrap ${
                        selectedService === idx
                          ? 'bg-green-600 text-white'
                          : 'bg-beige-100 text-black hover:bg-beige-400'
                      }`}
                    >
                      {service.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Service Details */}
              <div className="flex-1 flex flex-col">
                {/* Tabs */}
                <div className="bg-beige-200 border-b border-beige-300 flex">
                  {['code', 'dockerfile', 'openapi', 'endpoints'].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-4 py-2 border-b-2 ${
                        activeTab === tab
                          ? 'border-green-500 text-green-400'
                          : 'border-transparent text-black hover:text-black'
                      }`}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </div>

                {/* Tab Content */}
                <div className="flex-1 overflow-auto">
                  {activeTab === 'code' && (
                    <Editor
                      height="100%"
                      language="javascript"
                      value={result.microservices[selectedService].code}
                      theme="light"
                      options={{
                        readOnly: true,
                        minimap: { enabled: false },
                        fontSize: 14,
                      }}
                    />
                  )}

                  {activeTab === 'dockerfile' && (
                    <Editor
                      height="100%"
                      language="dockerfile"
                      value={result.microservices[selectedService].dockerfile}
                      theme="light"
                      options={{
                        readOnly: true,
                        minimap: { enabled: false },
                        fontSize: 14,
                      }}
                    />
                  )}

                  {activeTab === 'openapi' && (
                    <Editor
                      height="100%"
                      language="json"
                      value={JSON.stringify(result.microservices[selectedService].openapi_spec, null, 2)}
                      theme="light"
                      options={{
                        readOnly: true,
                        minimap: { enabled: false },
                        fontSize: 14,
                      }}
                    />
                  )}

                  {activeTab === 'endpoints' && (
                    <div className="p-6 space-y-4">
                      <h3 className="text-lg font-semibold mb-4">
                        API Endpoints ({result.microservices[selectedService].endpoints.length})
                      </h3>
                      {result.microservices[selectedService].endpoints.map((endpoint, idx) => (
                        <div
                          key={idx}
                          className="bg-beige-200 border border-beige-300 rounded-lg p-4"
                        >
                          <div className="flex items-center gap-3 mb-2">
                            <span className={`px-2 py-1 rounded text-xs font-mono ${
                              endpoint.method === 'GET' ? 'bg-green-600' :
                              endpoint.method === 'POST' ? 'bg-green-600' :
                              endpoint.method === 'PUT' ? 'bg-yellow-600' :
                              'bg-red-600'
                            }`}>
                              {endpoint.method}
                            </span>
                            <code className="text-green-400">{endpoint.path}</code>
                          </div>
                          <p className="text-sm text-black mb-2">{endpoint.description}</p>
                          {endpoint.params && endpoint.params.length > 0 && (
                            <div className="text-sm">
                              <span className="text-black">Parameters: </span>
                              <code className="text-green-400">{endpoint.params.join(', ')}</code>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
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
