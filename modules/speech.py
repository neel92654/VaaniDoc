import os
import io
import streamlit as st
from groq import Groq

# Map Indian languages to ISO language codes for Whisper hint if needed
LANGUAGE_CODE_MAP = {
    "Hindi": "hi",
    "Gujarati": "gu",
    "Marathi": "mr",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Odia": "or",
    "English": "en"
}

def get_groq_client():
    """Retrieve Groq client initialized with key from env or st.secrets."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
        
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured. Please set GROQ_API_KEY in your .env file or Streamlit Secrets.")
    
    return Groq(api_key=api_key)

def transcribe_audio(audio_bytes: bytes, language_name: str = "Hindi") -> str:
    """
    Transcribes audio bytes using Groq Whisper model `whisper-large-v3-turbo`.
    Preserves original regional language transcript.
    """
    if not audio_bytes or len(audio_bytes) == 0:
        raise ValueError("Audio buffer is empty. Please record audio before submitting.")

    try:
        client = get_groq_client()
        
        # Prepare named tuple/buffer for Groq client audio file upload
        audio_file = ("recording.wav", audio_bytes, "audio/wav")
        
        lang_code = LANGUAGE_CODE_MAP.get(language_name, None)
        
        kwargs = {
            "file": audio_file,
            "model": "whisper-large-v3-turbo",
            "temperature": 0.0
        }
        if lang_code:
            kwargs["language"] = lang_code

        transcription = client.audio.transcriptions.create(**kwargs)
        
        transcript_text = transcription.text.strip()
        if not transcript_text:
            raise ValueError("Transcription returned empty text. Please speak clearly into the microphone.")
            
        return transcript_text

    except Exception as e:
        # Re-raise clean error message for UI
        raise RuntimeError(f"Speech transcription failed: {str(e)}")
