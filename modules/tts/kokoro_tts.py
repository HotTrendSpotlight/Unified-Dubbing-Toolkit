"""
Kokoro TTS Implementation
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from .base import TTSBase


class KokoroTTS(TTSBase):
    """Kokoro TTS implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = "Kokoro TTS"
        self.description = "Kokoro text-to-speech system"
        self.supported_languages = ["en", "ja"]  # Kokoro primarily supports English and Japanese
        self.supported_voices = [
            "af_bella", "af_nicole", "af_sarah", "af_sky",
            "am_adam", "am_michael", "bf_emma", "bf_isabella",
            "bm_george", "bm_lewis"
        ]
        self.quality_levels = ["medium", "high"]
        self.requirements = ["kokoro"]
        self.model = None
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if Kokoro is available"""
        try:
            import kokoro
            return True
        except ImportError:
            return False
    
    async def synthesize(self, text: Union[str, Dict], output_file: str, 
                        language: str = "en", voice: Optional[str] = None,
                        quality: str = "medium", **kwargs) -> str:
        """Synthesize speech using Kokoro TTS"""
        if not self.is_available():
            raise RuntimeError("Kokoro TTS not available. Install kokoro package")
        
        # Handle transcript dict input
        if isinstance(text, dict):
            if "segments" in text:
                text = " ".join(segment.get("text", "") for segment in text["segments"])
            elif "text" in text:
                text = text["text"]
            else:
                raise ValueError("Invalid text format")
        
        if not text.strip():
            raise ValueError("Empty text provided")
        
        # Set default voice if not provided
        if voice is None:
            voice = "af_bella" if language == "en" else "af_bella"
        
        # Load model if needed
        if self.model is None:
            await self._load_model()
        
        # Run synthesis in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, 
            self._synthesize_sync, 
            text, 
            voice, 
            output_file,
            kwargs
        )
        
        return output_file
    
    async def _load_model(self):
        """Load Kokoro model"""
        import kokoro
        
        self.logger.info("Loading Kokoro model...")
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(
            None,
            kokoro.load_model
        )
    
    def _synthesize_sync(self, text: str, voice: str, output_file: str, kwargs: Dict):
        """Synchronous synthesis (runs in thread pool)"""
        import kokoro
        
        # Generate audio
        audio = kokoro.generate(
            text=text,
            voice=voice,
            **kwargs
        )
        
        # Save to file
        kokoro.save_audio(audio, output_file)
    
    def get_available_voices(self, language: Optional[str] = None) -> List[str]:
        """Get available voices for language"""
        if language == "ja":
            # Return Japanese-compatible voices (if any)
            return ["af_bella"]  # Kokoro may have limited Japanese support
        
        return self.supported_voices