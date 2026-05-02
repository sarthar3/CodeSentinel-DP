"""
Incident Debugger API Router
Enhanced incident triage with root cause analysis
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from ..incident_debugger.root_cause_analyzer import RootCauseAnalyzer

router = APIRouter()
analyzer = RootCauseAnalyzer()

class ErrorLogRequest(BaseModel):
    error_logs: str
    context: Optional[str] = None

class ExecutionTraceRequest(BaseModel):
    error_context: str
    codebase_context: Optional[str] = None

class RootCauseFixRequest(BaseModel):
    root_cause: str
    affected_components: List[str]

class SimilarIncidentRequest(BaseModel):
    current_incident: str
    historical_incidents: List[Dict[str, Any]]

@router.post("/analyze-logs")
async def analyze_error_logs(request: ErrorLogRequest):
    """
    Analyze error logs to identify root causes
    """
    try:
        analysis = await analyzer.analyze_error_logs(request.error_logs)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trace-execution")
async def trace_execution_flow(request: ExecutionTraceRequest):
    """
    Trace execution flow leading to error
    """
    try:
        trace = await analyzer.trace_execution_flow(
            request.error_context,
            request.codebase_context
        )
        return trace
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-fixes")
async def suggest_fixes(request: RootCauseFixRequest):
    """
    Suggest fixes for identified root cause
    """
    try:
        fixes = await analyzer.suggest_root_cause_fixes(
            request.root_cause,
            request.affected_components
        )
        return {"fixes": fixes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-similar")
async def find_similar_incidents(request: SimilarIncidentRequest):
    """
    Find similar historical incidents
    """
    try:
        similar = await analyzer.find_similar_incidents(
            request.current_incident,
            request.historical_incidents
        )
        return {"similar_incidents": similar}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/full-analysis")
async def full_incident_analysis(request: ErrorLogRequest):
    """
    Complete incident analysis pipeline
    """
    try:
        # Analyze logs
        analysis = await analyzer.analyze_error_logs(request.error_logs)
        
        # Trace execution
        trace = await analyzer.trace_execution_flow(
            request.error_logs,
            request.context
        )
        
        # Suggest fixes
        fixes = await analyzer.suggest_root_cause_fixes(
            analysis.get('root_cause', ''),
            analysis.get('affected_components', [])
        )
        
        # Generate report
        report = await analyzer.generate_incident_report(
            analysis,
            trace,
            fixes
        )
        
        return {
            "analysis": analysis,
            "execution_trace": trace,
            "suggested_fixes": fixes,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
