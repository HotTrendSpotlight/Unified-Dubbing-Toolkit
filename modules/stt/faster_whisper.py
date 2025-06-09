"""
Faster Whisper STT Implementation
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .base import STTBase


class FasterWhisper(STTBase):
    """Faster Whisper implementation using CTranslate2"""
    
    def __init__(self, model_size: str = "base", compute_type: str = "float16"):
        super().__init__()
        self.model_size = model_size
        self.compute_type = compute_type
        self.name = "Faster Whisper"
        self.description = "Faster Whisper implementation using CTranslate2"
        self.supported_languages = [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", 
            "ar", "hi", "tr", "pl", "nl", "sv", "da", "no", "fi"
        ]
        self.requirements = ["faster-whisper"]
        self.model = None
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if Faster Whisper is available"""
        try:
            from faster_whisper import WhisperModel
            return True
        except ImportError:
            return False
    
    async def transcribe(self, audio_file: str, language: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Transcribe audio using Faster Whisper"""
        if not self.is_available():
            raise RuntimeError("Faster Whisper not available. Install with: pip install faster-whisper")
        
        if not self.validate_audio_file(audio_file):
            raise ValueError(f"Unsupported audio format: {Path(audio_file).suffix}")
        
        # Load model if not already loaded
        if self.model is None:
            await self._load_model()
        
        # Run transcription in thread pool
        loop = asyncio.get_event_loop()
        segments, info = await loop.run_in_executor(
            None, 
            self._transcribe_sync, 
            audio_file, 
            language, 
            kwargs
        )
        
        return self._format_result(segments, info)
    
    async def _load_model(self):
        """Load Faster Whisper model"""
        from faster_whisper import WhisperModel
        
        self.logger.info(f"Loading Faster Whisper model: {self.model_size}")
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(
            None,
            lambda: WhisperModel(self.model_size, compute_type=self.compute_type)
        )
    
    def _transcribe_sync(self, audio_file: str, language: Optional[str], kwargs: Dict):
        """Synchronous transcription (runs in thread pool)"""
        segments, info = self.model.transcribe(
            audio_file,
            language=language,
            **kwargs
        )
        
        # Convert generator to list
        segments = list(segments)
        return segments, info
    
    def _format_result(self, segments, info) -> Dict[str, Any]:
        """Format Faster Whisper result to standard format"""
        formatted_segments = []
        full_text = ""
        
        for segment in segments:
            formatted_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "confidence": segment.avg_logprob
            })
            full_text += segment.text
        
        return {
            "text": full_text.strip(),
            "segments": formatted_segments,
            "language": info.language,
            "confidence": sum(s["confidence"] for s in formatted_segments) / len(formatted_segments) if formatted_segments else 0.0
        }