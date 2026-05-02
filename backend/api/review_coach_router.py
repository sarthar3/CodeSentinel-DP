"""
Review Coach API Router
Sentiment-aware code review assistance
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from ..review_coach.sentiment_analyzer import SentimentAnalyzer

router = APIRouter()
sentiment_analyzer = SentimentAnalyzer()

class CommentAnalysisRequest(BaseModel):
    comment: str

class CommentImprovementRequest(BaseModel):
    comment: str
    reviewer_style: str = "balanced"

class ReviewGenerationRequest(BaseModel):
    code_diff: str
    context: Optional[str] = None

class ReviewerStyleRequest(BaseModel):
    reviewer_id: str
    comments: List[str]

@router.post("/analyze-sentiment")
async def analyze_comment_sentiment(request: CommentAnalysisRequest):
    """
    Analyze sentiment of a code review comment
    """
    try:
        analysis = sentiment_analyzer.analyze_sentiment(request.comment)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/improve-comment")
async def improve_review_comment(request: CommentImprovementRequest):
    """
    Improve a code review comment to be more constructive
    """
    try:
        # Analyze sentiment first
        sentiment = sentiment_analyzer.analyze_sentiment(request.comment)
        
        # Improve if needed
        improved = await sentiment_analyzer.improve_comment(
            request.comment,
            sentiment,
            request.reviewer_style
        )
        
        return {
            "original": request.comment,
            "improved": improved,
            "sentiment_analysis": sentiment,
            "was_improved": improved != request.comment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-review")
async def generate_code_review(request: ReviewGenerationRequest):
    """
    Generate constructive code review feedback
    """
    try:
        feedback = await sentiment_analyzer.generate_review_feedback(
            request.code_diff,
            request.context or ""
        )
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-reviewer-style")
async def analyze_reviewer_style(request: ReviewerStyleRequest):
    """
    Analyze a reviewer's typical style from past comments
    """
    try:
        style_profile = sentiment_analyzer.track_reviewer_style(
            request.reviewer_id,
            request.comments
        )
        return style_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-improve")
async def batch_improve_comments(
    comments: List[str],
    reviewer_style: str = "balanced"
):
    """
    Improve multiple comments at once
    """
    try:
        results = []
        for comment in comments:
            sentiment = sentiment_analyzer.analyze_sentiment(comment)
            improved = await sentiment_analyzer.improve_comment(
                comment,
                sentiment,
                reviewer_style
            )
            results.append({
                "original": comment,
                "improved": improved,
                "sentiment": sentiment.get("overall_sentiment"),
                "needs_improvement": sentiment.get("needs_improvement")
            })
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
