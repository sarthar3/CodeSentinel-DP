"""
Code Explainer API Router
Accessible code explanations for non-technical stakeholders
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from ..code_explainer.explainer import CodeExplainer

router = APIRouter()
explainer = CodeExplainer()

class ExplainCodeRequest(BaseModel):
    code: str
    audience: str = "business"
    detail_level: str = "summary"

class ExecutiveSummaryRequest(BaseModel):
    repository_analysis: Dict[str, Any]
    recent_changes: List[str]

class TechnicalDecisionRequest(BaseModel):
    decision: str
    context: str
    audience: str = "business"

class WeeklyDigestRequest(BaseModel):
    changes: List[Dict[str, Any]]
    metrics: Dict[str, Any]

class ErrorTranslationRequest(BaseModel):
    error_message: str
    user_action: Optional[str] = None

@router.post("/explain")
async def explain_code(request: ExplainCodeRequest):
    """
    Explain code for specific audience
    """
    try:
        explanation = await explainer.explain_code(
            request.code,
            request.audience,
            request.detail_level
        )
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/executive-summary")
async def create_executive_summary(request: ExecutiveSummaryRequest):
    """
    Create executive summary of repository and changes
    """
    try:
        summary = await explainer.create_executive_summary(
            request.repository_analysis,
            request.recent_changes
        )
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain-decision")
async def explain_technical_decision(request: TechnicalDecisionRequest):
    """
    Explain a technical decision in accessible terms
    """
    try:
        explanation = await explainer.explain_technical_decision(
            request.decision,
            request.context,
            request.audience
        )
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weekly-digest")
async def generate_weekly_digest(request: WeeklyDigestRequest):
    """
    Generate weekly digest for stakeholders
    """
    try:
        digest = await explainer.generate_weekly_digest(
            request.changes,
            request.metrics
        )
        return {"digest": digest}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate-error")
async def translate_error_message(request: ErrorTranslationRequest):
    """
    Translate technical error into user-friendly message
    """
    try:
        translation = await explainer.translate_error_message(
            request.error_message,
            request.user_action
        )
        return translation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audiences")
async def get_available_audiences():
    """
    Get list of available audience types
    """
    return {
        "audiences": [
            {
                "id": "business",
                "name": "Business Stakeholders",
                "description": "Product managers, business analysts"
            },
            {
                "id": "executive",
                "name": "Executive Leadership",
                "description": "C-level executives, senior management"
            },
            {
                "id": "technical",
                "name": "Technical Team",
                "description": "Developers, engineers"
            },
            {
                "id": "general",
                "name": "General Audience",
                "description": "Anyone without technical background"
            }
        ],
        "detail_levels": [
            {
                "id": "summary",
                "name": "Summary",
                "description": "Brief 2-3 sentence overview"
            },
            {
                "id": "detailed",
                "name": "Detailed",
                "description": "Comprehensive explanation with examples"
            },
            {
                "id": "deep-dive",
                "name": "Deep Dive",
                "description": "In-depth technical analysis"
            }
        ]
    }

# Made with Bob
