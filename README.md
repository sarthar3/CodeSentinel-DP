# CodeSentinel DP (Developer Platform)

**The AI-powered developer lifecycle platform that understands, cleans, migrates, tests, triages, heals, and secures your projects — end to end.**

## 🎯 Overview

CodeSentinel DP is a unified AI-powered platform that solves 13 real enterprise problems in one continuous workflow. It demonstrates how AI can autonomously handle the entire recovery and modernization lifecycle of a legacy codebase and its data, with advanced features for voice interaction, automated documentation, incident debugging, code review coaching, and stakeholder communication.

## 🚀 Core Features

### 1. RAG ChatBot (Voice-Enabled + Transformer AI)
Voice-enabled AI assistant with **dual AI engines** - choose between Groq (fast) or DialoGPT transformers (deep learning). Features:
- **Dual AI Modes**:
  - 🚀 **Groq Mode**: Lightning-fast responses with Llama 3.3 70B (default)
  - 🧠 **Transformer Mode**: Deep learning with DialoGPT + BERT embeddings for conversational AI
- **Voice Input**: Click microphone and speak naturally - auto-sends after 2 seconds of silence
- **Voice Output**: Toggle voice responses on/off for hands-free interaction
- **Enhanced RAG**: Better semantic search with BERT (all-mpnet-base-v2) embeddings
- **Wikipedia Integration**: Enrich knowledge base with Wikipedia articles on-demand
- **Real-time Transcription**: See your speech converted to text in real-time
- **Browser-based Speech**: Uses Web Speech API (Chrome/Edge) - no server-side speech processing needed

**AI Models:**
- **Groq**: Llama 3.3 70B (fast, cloud-based)
- **Transformers**: DialoGPT-medium + BERT (local, conversational)
- **Embeddings**: all-mpnet-base-v2 (better than MiniLM)

**Perfect for:** Hands-free code review, rapid onboarding, accessibility, multitasking developers, and offline AI

### 2. Code Explainer
Translates technical code into plain English for executives, product managers, and business stakeholders. Adapts explanation depth to audience.

**AI Engine:** Groq API (Llama 3.3 70B) | **Voice:** Web Speech API (TTS)

### 3. Autonomous QA Agent
Auto-generate unit tests, integration tests, and coverage reports for codebases using CodeLlama.

**AI Engine:** Groq API (CodeLlama 34B) | **Analysis:** AST parsing + AI generation

### 4. Automated Issue Triage
Analyze GitHub issues, assign severity, and link to similar past incidents using RAG.

**AI Engine:** Groq API (Llama 3.3 70B) | **RAG:** ChromaDB + LangChain

### 5. Incident Debugger
Paste error logs and get instant root cause analysis with execution flow tracing and actionable fixes. Finds similar historical incidents.

**AI Engine:** Groq API (Llama 3.3 70B) | **RAG:** ChromaDB + LangChain

### 6. Review Coach
Analyzes sentiment in code review comments and rewrites harsh feedback into constructive, actionable suggestions. Generates AI-powered reviews.

**AI Engine:** Groq API (Llama 3.3 70B) | **Sentiment:** TextBlob + VADER

### 7. Dataset Cleaner
Automated cleaning, handling missing values, and numerical encoding for ML readiness.

**AI Engine:** Pandas + Scikit-Learn | **Analysis:** Statistical profiling

### 8. DB Schema Optimizer
Analyze and normalize SQL database schemas with AI-powered normalization recommendations.

**AI Engine:** Frontend-only logic | **Analysis:** SQL parsing + normalization rules

### 9. Repo V-Assist (Voice-Driven Repository Assistant)
Speak your questions and get instant voice responses about your codebase. Perfect for hands-free code exploration and rapid onboarding.

**AI Engine:** Groq API (Llama 3.3 70B) | **Voice:** Web Speech API (Browser-based)

## ✨ Advanced Features

### 10. Legacy Code Porter
Analyze legacy monoliths and generate modern microservices with Docker + OpenAPI.

**AI Engine:** Groq API (Llama 3.3 70B) | **Analysis:** AST parsing + microservice generation

### 11. Self-Healing CI/CD
Monitor CI/CD runs, detect failures, parse logs via LLM, and auto-generate fix patches.

**AI Engine:** Groq API (Llama 3.3 70B) | **Analysis:** Log parsing + patch generation

### 12. AI Model Suggester
Analyze preprocessed datasets and project context to receive AI-powered algorithm recommendations.

**AI Engine:** Groq API (Llama 3.3 70B) | **Analysis:** Dataset profiling + ML recommendations

### 13. Doc & Test Pipeline
Automatically generate documentation and unit tests when code changes. AI-powered classification and routing.

**AI Engine:** Groq API (CodeLlama 34B) | **Analysis:** AST parsing + AI generation

## 🏗️ Architecture

### Core Features Pipeline
```
RAG ChatBot → Code Explainer → QA Agent
    ↓              ↓              ↓
Triage → Incident Debugger → Review Coach
    ↓              ↓              ↓
Dataset Cleaner → DB Optimizer → Repo V-Assist
```

### Advanced Features Pipeline
```
Code Porter → CI/CD Healer → Model Suggester → Doc & Test Pipeline
```

## 🛠️ Tech Stack

- **Backend**: Python 3.11 + FastAPI
- **AI Engines**:
  - **Groq API**: Llama 3.3 70B, CodeLlama 34B (Fast & Free)
  - **Transformers**: DialoGPT-medium, BERT (PyTorch-based)
- **Speech**: Web Speech API (Browser-based STT/TTS)
- **Sentiment**: TextBlob, VADER Sentiment
- **Data Science**: Pandas, Scikit-Learn, Joblib
- **Vector DB**: ChromaDB (local)
- **RAG**: LangChain + Sentence Transformers (all-mpnet-base-v2)
- **Deep Learning**: PyTorch 2.11+, Transformers 4.35+
- **Knowledge**: Wikipedia API integration
- **Frontend**: React 18 + Vite, TailwindCSS, Monaco Editor, Lucide Icons
- **Database**: SQLite (local)

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git installed

### Setup

1. Clone the repository:
```bash
git clone https://github.com/sarthar3/CodeSentinel-DP.git
cd CodeSentinel-DP
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` and add your API keys:
```
GROQ_API_KEY=your_groq_key
# Optional for IBM Watson features
WATSON_API_KEY=your_watson_key
WATSON_URL=your_watson_url
# Optional for Google Search / Gemini features
GOOGLE_API_KEY=your_google_key
```

4. Install dependencies:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install --legacy-peer-deps --force
```

## 🚀 Running the Application

### Backend
```bash
cd backend
python -m uvicorn backend.api.main:app --reload
```
Available at http://localhost:8000

### Frontend
```bash
cd frontend
npm run dev
```
Available at http://localhost:5173

## 🏆 Project Highlights

- **13-Feature Platform**: Complete developer lifecycle from documentation to deployment
- **RAG-Powered**: Hallucination-free responses with source citations
- **Multi-Language**: Supports Python, JavaScript, TypeScript, Java, Go, and more
- **Real-time Analysis**: Instant code analysis and recommendations
- **Voice Interaction**: Hands-free code review and onboarding
- **Public Interface**: No authentication required for rapid local development
- **Persistent History**: All interactions stored locally in SQLite
- **AI-Driven Logic**: Each feature uses tailored prompts and RAG
- **Streaming Responses**: Real-time AI output for better UX
- **Extensible Architecture**: Easy to add new features and integrations

## 📄 License
MIT License
