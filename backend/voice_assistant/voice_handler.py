"""
Voice Handler for Speech-to-Text and Text-to-Speech
Integrates with IBM Watson and local speech services
"""
import os
import io
import base64
from typing import Optional, Dict, Any
from gtts import gTTS
import tempfile
from groq import Groq

class VoiceHandler:
    """Handles voice input/output for the assistant"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.watson_available = self._check_watson_credentials()
        
    def _check_watson_credentials(self) -> bool:
        """Check if Watson credentials are available"""
        return bool(os.getenv("WATSON_API_KEY") and os.getenv("WATSON_URL"))
    
    async def transcribe_audio(self, audio_data: bytes, format: str = "wav") -> str:
        """
        Transcribe audio to text using Groq Whisper
        
        Args:
            audio_data: Audio file bytes
            format: Audio format (wav, mp3, etc.)
            
        Returns:
            Transcribed text
        """
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name
            
            # Use Groq Whisper for transcription
            with open(temp_audio_path, "rb") as audio_file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="text"
                )
            
            # Clean up temp file
            os.unlink(temp_audio_path)
            
            return transcription
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    async def synthesize_speech(self, text: str, language: str = "en") -> bytes:
        """
        Convert text to speech using gTTS
        
        Args:
            text: Text to convert
            language: Language code (en, es, fr, etc.)
            
        Returns:
            Audio bytes (MP3 format)
        """
        try:
            # Create speech using gTTS
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
            
        except Exception as e:
            raise Exception(f"Speech synthesis failed: {str(e)}")
    
    async def analyze_intent(self, text: str) -> Dict[str, Any]:
        """
        Analyze user intent from transcribed text using Groq
        
        Args:
            text: User's spoken text
            
        Returns:
            Intent analysis with action and parameters
        """
        try:
            prompt = f"""Analyze the following developer question and extract:
1. Primary intent (code_review, onboarding, explanation, navigation)
2. Specific action requested
3. Any mentioned file paths, functions, or code elements
4. Context needed

User input: "{text}"

Respond in JSON format:
{{
    "intent": "intent_type",
    "action": "specific_action",
    "entities": {{"files": [], "functions": [], "topics": []}},
    "context": "brief context"
}}"""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "intent": "unknown",
                "action": "clarify",
                "entities": {},
                "context": str(e)
            }

# Made with Bob
