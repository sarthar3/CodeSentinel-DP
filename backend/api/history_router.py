from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..database.models import ChatHistory
from .schemas import HistoryCreate, HistoryResponse

router = APIRouter()

@router.post("/", response_model=HistoryResponse)
def save_history(history: HistoryCreate, db: Session = Depends(get_db)):
    new_history = ChatHistory(
        query=history.query,
        answer=history.answer
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    return new_history

@router.get("/", response_model=List[HistoryResponse])
def get_history(db: Session = Depends(get_db)):
    history = db.query(ChatHistory).order_by(ChatHistory.created_at.asc()).all()
    return history
