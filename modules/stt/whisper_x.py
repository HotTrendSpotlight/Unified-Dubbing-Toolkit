"""
WhisperX STT Implementation
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .base import STTBase


class WhisperX(STTBase):
    """WhisperX implementation with speaker diarization and word-level timestamps"""
    
    def __init__(self, model_size: str = "base", compute_type: str = "float16"):
        super().__init__()
        self.model_size = model_size
        self.compute_type = compute_type
        self.name = "WhisperX"
        self.description = "WhisperX with speaker diarization and word-level timestamps"
        self.supported_languages = [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", 
            "ar", "hi", "tr", "pl", "nl", "sv", "da", "no", "fi"
        ]
        self.requirements = ["whisperx"]
        self.model = None
        self.align_model = None
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if WhisperX is available"""
        try:
            import whisperx
            return True
        except ImportError:
            return False
    
    async def transcribe(self, audio_file: str, language: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Transcribe audio using WhisperX"""
        if not self.is_available():
            raise RuntimeError("WhisperX not available. Install with: pip install whisperx")
        
        if not self.validate_audio_file(audio_file):
            raise ValueError(f"Unsupported audio format: {Path(audio_file).suffix}")
        
        # Load models if not already loaded
        if self.model is None:
            await self._load_models()
        
        # Run transcription in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            self._transcribe_sync, 
            audio_file, 
            language, 
            kwargs
        )
        
        return self._format_result(result)
    
    async def _load_models(self):
        """Load WhisperX models"""
        import whisperx
        
        self.logger.info(f"Loading WhisperX model: {self.model_size}")
        loop = asyncio.get_event_loop()
        
        # Load transcription model
        self.model = await loop.run_in_executor(
            None,
            lambda: whisperx.load_model(self.model_size, compute_type=self.compute_type)
        )
    
    def _transcribe_sync(self, audio_file: str, language: Optional[str], kwargs: Dict):
        """Synchronous transcription (runs in thread pool)"""
        import whisperx
        
        # Load audio
        audio = whisperx.load_audio(audio_file)
        
        # Transcribe
        result = self.model.transcribe(audio, language=language, **kwargs)
        
        # Load alignment model if language is detected/specified
        detected_language = result.get("language", language)
        if detected_language and self.align_model is None:
            try:
                self.align_model, metadata = whisperx.load_align_model(
                    language_code=detected_language, 
                    device=self.model.device
                )
                
                # Align whisper output
                result = whisperx.align(
                    result["segments"], 
                    self.align_model, 
                    metadata, 
                    audio, 
                    device=self.model.device, 
                    return_char_alignments=False
                )
            except Exception as e:
                self.logger.warning(f"Failed to load alignment model: {e}")
        
        return result
    
    def _format_result(self, whisperx_result) -> Dict[str, Any]:
        """Format WhisperX result to standard format"""
        if isinstance(whisperx_result, dict) and "segments" in whisperx_result:
            segments = whisperx_result["segments"]
            language = whisperx_result.get("language", "unknown")
        else:
            segments = whisperx_result.get("segments", [])
            language = "unknown"
        
        formatted_segments = []
        full_text = ""
        
        for segment in segments:
            text = segment.get("text", "").strip()
            formatted_segments.append({
                "start": segment.get("start", 0.0),
                "end": segment.get("end", 0.0),
                "text": text,
                "confidence": segment.get("score", 0.0),
                "words": segment.get("words", [])  # Word-level timestamps if available
            })
            full_text += text + " "
        
        return {
            "text": full_text.strip(),
            "segments": formatted_segments,
            "language": language,
            "confidence": sum(s["confidence"] for s in formatted_segments) / len(formatted_segments) if formatted_segments else 0.0
        }