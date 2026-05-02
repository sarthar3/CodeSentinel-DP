"""
FastAPI router for Triage Agent endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
import asyncio

from .schemas import TriageRequest, TriageResponse, TriageResult, SeverityLevel, RAGSource
from ..triage.agent import TriageAgent

router = APIRouter()

# Initialize triage agent
triage_agent = TriageAgent()


@router.post("/analyze", response_model=TriageResponse)
async def analyze_issue(request: TriageRequest):
    """
    Analyze and triage a GitHub issue
    
    Args:
        request: Triage request with issue details
        
    Returns:
        Triage analysis with severity and recommendations
    """
    try:
        # Query RAG for similar incidents
        similar_incidents = []
        try:
            from ..rag.query import RAGQueryEngine
            rag_engine = RAGQueryEngine()
            
            # Search for similar incidents
            query = f"{request.issue_title} {request.issue_body[:200]}"
            similar_docs = rag_engine.retrieve_similar(query, top_k=3)
            similar_incidents = similar_docs
        except Exception as e:
            print(f"RAG query failed: {e}")
            # Continue without RAG results
        
        # Perform triage
        result = triage_agent.triage_issue(
            request.issue_title,
            request.issue_body,
            request.issue_number,
            similar_incidents
        )
        
        # Convert to schema format
        triage_result = TriageResult(
            severity=SeverityLevel(result["severity"]),
            category=result["category"],
            root_cause=result["root_cause"],
            similar_incidents=[
                RAGSource(**inc) for inc in result["similar_incidents"]
            ],
            reproduction_steps=result.get("reproduction_steps"),
            recommended_action=result["recommended_action"]
        )
        
        return TriageResponse(
            triage=triage_result,
            comment_posted=False  # Would be True if actually posting to GitHub
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/webhook")
async def github_webhook(payload: dict):
    """
    GitHub webhook endpoint for automatic triage
    
    Args:
        payload: GitHub webhook payload
        
    Returns:
        Webhook processing result
    """
    try:
        # Verify webhook signature (simplified for demo)
        # In production, verify HMAC signature
        
        action = payload.get("action")
        issue = payload.get("issue", {})
        
        if action == "opened" and issue:
            # Triage the new issue
            request = TriageRequest(
                issue_title=issue.get("title", ""),
                issue_body=issue.get("body", ""),
                issue_number=issue.get("number", 0)
            )
            
            # Process asynchronously
            result = await analyze_issue(request)
            
            # In production, post comment to GitHub using PyGithub
            # github_client.post_comment(issue_number, triage_comment)
            
            return {
                "status": "processed",
                "issue_number": issue.get("number"),
                "severity": result.triage.severity,
                "comment_posted": False  # Would be True in production
            }
        
        return {"status": "ignored", "action": action}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if Triage Agent is ready"""
    return {
        "status": "healthy",
        "rag_integration": "enabled",
        "github_integration": "demo_mode"
    }

# Made with Bob
