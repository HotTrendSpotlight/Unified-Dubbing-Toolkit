"""
Bark TTS Implementation
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from .base import TTSBase


class BarkTTS(TTSBase):
    """Bark TTS implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = "Bark TTS"
        self.description = "Bark text-to-speech model by Suno AI"
        self.supported_languages = [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", 
            "ar", "hi", "tr", "pl", "nl", "sv", "da", "no", "fi"
        ]
        self.supported_voices = [
            "v2/en_speaker_0", "v2/en_speaker_1", "v2/en_speaker_2", 
            "v2/en_speaker_3", "v2/en_speaker_4", "v2/en_speaker_5",
            "v2/en_speaker_6", "v2/en_speaker_7", "v2/en_speaker_8", "v2/en_speaker_9"
        ]
        self.quality_levels = ["medium", "high"]  # Bark doesn't have low quality
        self.requirements = ["bark", "torch", "transformers"]
        self.model = None
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if Bark is available"""
        try:
            from bark import SAMPLE_RATE, generate_audio, preload_models
            return True
        except ImportError:
            return False
    
    async def synthesize(self, text: Union[str, Dict], output_file: str, 
                        language: str = "en", voice: Optional[str] = None,
                        quality: str = "medium", **kwargs) -> str:
        """Synthesize speech using Bark TTS"""
        if not self.is_available():
            raise RuntimeError("Bark TTS not available. Install with: pip install bark")
        
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
            voice = "v2/en_speaker_6"
        
        # Load models if needed
        if self.model is None:
            await self._load_models()
        
        # Run synthesis in thread pool
        loop = asyncio.get_event_loop()
        audio_array = await loop.run_in_executor(
            None, 
            self._synthesize_sync, 
            text, 
            voice, 
            kwargs
        )
        
        # Save audio to file
        await self._save_audio(audio_array, output_file)
        
        return output_file
    
    async def _load_models(self):
        """Load Bark models"""
        from bark import preload_models
        
        self.logger.info("Loading Bark models...")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, preload_models)
        self.model = True  # Mark as loaded
    
    def _synthesize_sync(self, text: str, voice: str, kwargs: Dict):
        """Synchronous synthesis (runs in thread pool)"""
        from bark import generate_audio
        
        # Split long text into chunks if needed
        max_length = kwargs.get("max_length", 250)
        if len(text) > max_length:
            chunks = self._split_text(text, max_length)
            audio_chunks = []
            
            for chunk in chunks:
                audio_chunk = generate_audio(chunk, history_prompt=voice)
                audio_chunks.append(audio_chunk)
            
            # Concatenate audio chunks
            import numpy as np
            return np.concatenate(audio_chunks)
        else:
            return generate_audio(text, history_prompt=voice)
    
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks for long synthesis"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _save_audio(self, audio_array, output_file: str):
        """Save audio array to file"""
        from bark import SAMPLE_RATE
        import scipy.io.wavfile as wavfile
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: wavfile.write(output_file, SAMPLE_RATE, audio_array)
        )
    
    def get_available_voices(self, language: Optional[str] = None) -> List[str]:
        """Get available voices for language"""
        if language is None or language == "en":
            return self.supported_voices
        
        # For other languages, return generic voices
        # Bark supports multilingual but voice selection is limited
        return ["v2/en_speaker_6"]  # Default voice works for most languages