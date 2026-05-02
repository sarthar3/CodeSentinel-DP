# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project: CodeSentinel
AI-powered developer and data lifecycle platform solving 9 enterprise problems in one continuous workflow.

## Stack
- Backend: Python 3.11 + FastAPI, Groq API (llama-3-70b, CodeLlama-34b)
- Data: Pandas, Scikit-Learn (Cleaning & Preprocessing)
- Vector DB: ChromaDB (local), RAG: LangChain
- Frontend: React 18 + Vite, TailwindCSS (Beige Theme)

## Critical Architecture
13-feature pipeline organized into Core and Advanced capabilities:

### Core Features
1. **RAG ChatBot**: ChromaDB + citation-enforcing prompts + Voice + Transformers.
2. **Code Explainer**: Technical to plain-English translation for stakeholders.
3. **QA Agent**: Auto-generate unit/integration tests with CodeLlama.
4. **Triage**: Automated issue analysis and RAG integration.
5. **Incident Debugger**: Root cause analysis and execution flow tracing.
6. **Review Coach**: Sentiment-aware code review rewrites.
7. **Dataset Cleaner**: Handle nulls, duplicates, and numerical encoding.
8. **DB Optimizer**: SQL schema normalization recommendations.
9. **Repo V-Assist**: Voice-driven repository assistant (STT/TTS).

### Advanced Features
10. **Code Porter**: Legacy code analysis and microservice generation.
11. **CI/CD Healer**: Auto-patch build failures and log parsing.
12. **Model Suggester**: AI-driven algorithm recommendation.
13. **Doc & Test Pipeline**: Automated documentation and test generation on change.

## Commands
```bash
# Backend
python -m uvicorn backend.api.main:app --reload

# Frontend
cd frontend
npm run dev

# Dataset Ingestion
python backend/rag/ingest.py --dir <data_dir>
```

## Code Style
- RAG responses MUST include source citations.
- All Groq/Gemini calls use streaming where applicable.
- React components use the **Beige Theme** (bg-beige-200, border-beige-300).
- No authentication middleware (public single-user mode).

## Critical Patterns
- **History**: GET /api/history returns global interaction history.
- **Cleaning**: POST /api/cleaner/clean returns CSV and .pkl paths.
- **Suggestion**: POST /api/suggester/suggest returns AI markdown recommendation.
- **Optimization**: Frontend-only logic in `src/utils/schema/`.

## Bob Integration Requirements
- Use Plan mode before each stage implementation.
- Use Code mode for implementation.
- Run /review before every commit.
- Export sessions to /bob_sessions/.