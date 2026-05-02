"""
FastAPI main application entry point for CodeSentinel
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

from ..database.database import engine, SessionLocal
from ..database.models import Base, ChatHistory


# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="CodeSentinel API",
    description="AI-powered developer lifecycle platform",
    version="1.0.0"
)

# Initialize DB
Base.metadata.create_all(bind=engine)

async def cleanup_history_task():
    while True:
        try:
            db = SessionLocal()
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            db.query(ChatHistory).filter(ChatHistory.created_at < thirty_days_ago).delete()
            db.commit()
            db.close()
        except Exception as e:
            print(f"Error in cleanup task: {e}")
        await asyncio.sleep(86400) # Run once a day

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_history_task())

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CodeSentinel API",
        "version": "2.0.0",
        "core_features": {
            "rag": "🤖 RAG ChatBot (Voice + Transformers)",
            "explainer": "Code Explainer for Stakeholders",
            "qa": "Autonomous QA Agent",
            "triage": "Automated Issue Triage",
            "incident": "Incident Debugger & Root Cause Analysis",
            "review": "Sentiment-Aware Review Coach",
            "cleaner": "AI-Driven Dataset Cleaner",
            "schema": "DB Schema Optimizer",
            "voice": "Repo V-Assist (Voice-Driven Assistant)"
        },
        "advanced_features": {
            "porter": "Legacy Code Porter & Microservice Generator",
            "cicd": "Self-Healing CI/CD Healer",
            "suggester": "AI Model Suggester",
            "doc_test": "Doc & Test Automation Pipeline"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

from .history_router import router as history_router
from .rag_router import router as rag_router
from .porter_router import router as porter_router
from .qa_router import router as qa_router
from .triage_router import router as triage_router
from .dataset_cleaner_router import router as cleaner_router
from .model_suggester_router import router as suggester_router
from .voice_assistant_router import router as voice_router
from .doc_test_router import router as doc_test_router
from .incident_debugger_router import router as incident_router
from .review_coach_router import router as review_router
from .code_explainer_router import router as explainer_router

app.include_router(history_router, prefix="/api/history", tags=["History"])
app.include_router(rag_router, prefix="/api/rag", tags=["RAG"])
app.include_router(porter_router, prefix="/api/porter", tags=["Porter"])
app.include_router(qa_router, prefix="/api/qa", tags=["QA Agent"])
app.include_router(triage_router, prefix="/api/triage", tags=["Triage"])
app.include_router(cleaner_router, prefix="/api/cleaner", tags=["Dataset Cleaner"])
app.include_router(suggester_router, prefix="/api/suggester", tags=["Model Suggester"])
app.include_router(voice_router, prefix="/api/voice", tags=["Repo V-Assist"])
app.include_router(doc_test_router, prefix="/api/doc-test", tags=["Documentation & Testing"])
app.include_router(incident_router, prefix="/api/incident", tags=["Incident Debugger"])
app.include_router(review_router, prefix="/api/review", tags=["Review Coach"])
app.include_router(explainer_router, prefix="/api/explainer", tags=["Code Explainer"])
# app.include_router(cicd_router, prefix="/api/cicd", tags=["CI/CD Healer"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
