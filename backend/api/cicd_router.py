"""
CI/CD Healer Router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..cicd_healer.healer import CICDHealer

router = APIRouter()
healer = CICDHealer()

class BuildHealRequest(BaseModel):
    log: str
    build_id: Optional[str] = "manual_trigger"
    repo_url: Optional[str] = None

@router.post("/heal")
async def heal_build(request: BuildHealRequest):
    """
    Analyze failing build log and suggest fixes
    """
    if not request.log:
        raise HTTPException(status_code=400, detail="Build log is required")
        
    try:
        result = await healer.heal_build(request.log)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_healing_history():
    """
    Mocked history for demo purposes
    """
    return [
        {
            "id": "heal_141",
            "timestamp": "2024-05-01T14:30:00Z",
            "error_type": "Dependency",
            "status": "success",
            "confidence": 0.95
        },
        {
            "id": "heal_138",
            "timestamp": "2024-05-01T10:15:00Z",
            "error_type": "Syntax",
            "status": "success",
            "confidence": 0.88
        }
    ]

# Made with Bob
