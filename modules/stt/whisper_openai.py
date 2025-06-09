"""
OpenAI Whisper STT Implementation
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .base import STTBase


class WhisperOpenAI(STTBase):
    """OpenAI Whisper implementation"""
    
    def __init__(self, model_size: str = "base"):
        super().__init__()
        self.model_size = model_size
        self.name = "OpenAI Whisper"
        self.description = "OpenAI's Whisper automatic speech recognition system"
        self.supported_languages = [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", 
            "ar", "hi", "tr", "pl", "nl", "sv", "da", "no", "fi"
        ]
        self.requirements = ["openai-whisper", "torch"]
        self.model = None
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if Whisper is available"""
        try:
            import whisper
            return True
        except ImportError:
            return False
    
    async def transcribe(self, audio_file: str, language: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper"""
        if not self.is_available():
            raise RuntimeError("OpenAI Whisper not available. Install with: pip install openai-whisper")
        
        if not self.validate_audio_file(audio_file):
            raise ValueError(f"Unsupported audio format: {Path(audio_file).suffix}")
        
        # Load model if not already loaded
        if self.model is None:
            await self._load_model()
        
        # Run transcription in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            self._transcribe_sync, 
            audio_file, 
            language, 
            kwargs
        )
        
        return self._format_result(result)
    
    async def _load_model(self):
        """Load Whisper model"""
        import whisper
        
        self.logger.info(f"Loading Whisper model: {self.model_size}")
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(
            None, 
            whisper.load_model, 
            self.model_size
        )
    
    def _transcribe_sync(self, audio_file: str, language: Optional[str], kwargs: Dict) -> Dict:
        """Synchronous transcription (runs in thread pool)"""
        options = {
            "language": language,
            "task": "transcribe",
            **kwargs
        }
        
        # Remove None values
        options = {k: v for k, v in options.items() if v is not None}
        
        return self.model.transcribe(audio_file, **options)
    
    def _format_result(self, whisper_result: Dict) -> Dict[str, Any]:
        """Format Whisper result to standard format"""
        segments = []
        
        for segment in whisper_result.get("segments", []):
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "confidence": segment.get("avg_logprob", 0.0)
            })
        
        return {
            "text": whisper_result["text"].strip(),
            "segments": segments,
            "language": whisper_result.get("language", "unknown"),
            "confidence": sum(s["confidence"] for s in segments) / len(segments) if segments else 0.0
        }