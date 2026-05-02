# CodeSentinel DP - Quick Start Guide

## Prerequisites

Before you begin, ensure you have:
- **Python 3.11+** installed
- **Node.js 18+** installed
- **Git** installed
- **Groq API Key** (free tier from https://console.groq.com)

## Step-by-Step Setup

### 1. Configure Environment

1. Visit https://console.groq.com and get a free API key.
2. Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
3. Edit `.env` and add your `GROQ_API_KEY`.

### 2. Setup Backend

```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Start the backend server (from project root)
cd ..
python -m uvicorn backend.api.main:app --reload
```
The backend will start at: **http://localhost:8000**

### 3. Setup Frontend

```bash
cd frontend
# Install dependencies
npm install --legacy-peer-deps --force

# Start the development server
npm run dev
```
The frontend will start at: **http://localhost:5173**

## Features & Usage

### Core Features
1. **RAG ChatBot**: Dual AI engines (Groq + Transformers) with voice support for documentation queries.
2. **Code Explainer**: Translates complex code into plain English for non-technical stakeholders.
3. **QA Agent**: Autonomous unit and integration test generation using CodeLlama.
4. **Triage**: Automated issue analysis, severity assignment, and RAG-based linkage.
5. **Incident Debugger**: Root cause analysis and execution flow tracing for error logs.
6. **Review Coach**: Sentiment-aware code review feedback and constructive rewrites.
7. **Dataset Cleaner**: ML-ready data preprocessing, handling nulls and encoding.
8. **DB Optimizer**: AI-driven SQL schema normalization and architectural recommendations.
9. **Repo V-Assist**: Voice-driven repository assistant for hands-free code exploration.

### Advanced Features
10. **Code Porter**: Migrate legacy monoliths to modern microservices with Docker/OpenAPI.
11. **CI/CD Healer**: Self-healing pipelines that detect failures and auto-generate patches.
12. **Model Suggester**: AI-powered ML algorithm recommendations based on dataset profiling.
13. **Doc & Test Pipeline**: Automated documentation and test generation on every code change.

## Troubleshooting

- **Import Errors**: Ensure you start the backend from the **project root** directory.
- **API Errors**: Verify your `GROQ_API_KEY` is valid and has not reached its rate limit.
- **CORS Errors**: The backend is configured to allow all origins by default in development mode.

---
**CodeSentinel DP — Integrated AI Developer Lifecycle Platform**
