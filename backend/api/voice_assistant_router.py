"""
Repo V-Assist API Router
Handles voice-driven code review and onboarding requests
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io

from ..voice_assistant.voice_handler import VoiceHandler
from ..voice_assistant.onboarding_assistant import OnboardingAssistant

router = APIRouter()
voice_handler = VoiceHandler()
onboarding_assistant = OnboardingAssistant()

class VoiceQueryRequest(BaseModel):
    text: str
    repo_path: str

class OnboardingRequest(BaseModel):
    repo_path: str

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio to text using Groq Whisper
    """
    try:
        audio_data = await audio.read()
        transcription = await voice_handler.transcribe_audio(audio_data)
        
        # Analyze intent
        intent = await voice_handler.analyze_intent(transcription)
        
        return {
            "transcription": transcription,
            "intent": intent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/synthesize")
async def synthesize_speech(request: VoiceQueryRequest):
    """
    Convert text to speech
    """
    try:
        audio_bytes = await voice_handler.synthesize_speech(request.text)
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-repository")
async def analyze_repository(request: OnboardingRequest):
    """
    Analyze repository structure for onboarding
    """
    try:
        analysis = await onboarding_assistant.analyze_repository(request.repo_path)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/onboarding-query")
async def onboarding_query(request: VoiceQueryRequest):
    """
    Answer onboarding questions with voice support
    """
    try:
        # Get repository context
        repo_context = await onboarding_assistant.analyze_repository(request.repo_path)
        
        # Generate response
        response_text = await onboarding_assistant.generate_onboarding_response(
            request.text,
            repo_context
        )
        
        return {
            "text": response_text,
            "repo_context": repo_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-conversation")
async def voice_conversation(
    audio: UploadFile = File(...),
    repo_path: str = Form(...)
):
    """
    Complete voice conversation flow: transcribe -> process -> synthesize
    """
    try:
        # Transcribe audio
        audio_data = await audio.read()
        transcription = await voice_handler.transcribe_audio(audio_data)
        
        # Get repository context
        repo_context = await onboarding_assistant.analyze_repository(repo_path)
        
        # Generate response
        response_text = await onboarding_assistant.generate_onboarding_response(
            transcription,
            repo_context
        )
        
        # Synthesize response
        audio_response = await voice_handler.synthesize_speech(response_text)
        
        return {
            "transcription": transcription,
            "response_text": response_text,
            "audio_available": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
