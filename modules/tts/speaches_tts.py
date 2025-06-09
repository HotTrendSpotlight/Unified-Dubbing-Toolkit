"""
Speaches TTS Implementation
"""

import asyncio
import logging
import requests
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from .base import TTSBase


class SpeachesTTS(TTSBase):
    """Speaches TTS implementation"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        super().__init__()
        self.api_url = api_url
        self.name = "Speaches TTS"
        self.description = "Speaches text-to-speech API"
        self.supported_languages = [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", 
            "ar", "hi", "tr", "pl", "nl", "sv", "da", "no", "fi"
        ]
        self.supported_voices = []  # Will be populated from API
        self.quality_levels = ["low", "medium", "high"]
        self.requirements = ["speaches-tts server"]
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if Speaches TTS API is available"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    async def synthesize(self, text: Union[str, Dict], output_file: str, 
                        language: str = "en", voice: Optional[str] = None,
                        quality: str = "medium", **kwargs) -> str:
        """Synthesize speech using Speaches TTS API"""
        if not self.is_available():
            raise RuntimeError("Speaches TTS API not available. Start the speaches-tts server")
        
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
        
        # Get available voices if not cached
        if not self.supported_voices:
            await self._load_voices()
        
        # Set default voice if not provided
        if voice is None:
            voice = self._select_voice(language, quality)
        
        # Run synthesis
        await self._synthesize_async(text, voice, output_file, language, kwargs)
        
        return output_file
    
    async def _load_voices(self):
        """Load available voices from API"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(f"{self.api_url}/voices", timeout=10)
            )
            
            if response.status_code == 200:
                voices_data = response.json()
                self.supported_voices = [voice["id"] for voice in voices_data.get("voices", [])]
            
        except Exception as e:
            self.logger.warning(f"Failed to load voices from API: {e}")
            # Use default voices
            self.supported_voices = ["default"]
    
    def _select_voice(self, language: str, quality: str) -> str:
        """Select appropriate voice for language and quality"""
        # Filter voices by language if possible
        language_voices = [v for v in self.supported_voices if language in v.lower()]
        
        if language_voices:
            # Try to find quality-specific voice
            quality_voices = [v for v in language_voices if quality in v.lower()]
            return quality_voices[0] if quality_voices else language_voices[0]
        
        # Fallback to first available voice
        return self.supported_voices[0] if self.supported_voices else "default"
    
    async def _synthesize_async(self, text: str, voice: str, output_file: str, 
                              language: str, kwargs: Dict):
        """Run Speaches synthesis asynchronously"""
        payload = {
            "text": text,
            "voice": voice,
            "language": language,
            "quality": kwargs.get("quality", "medium"),
            "speed": kwargs.get("speed", 1.0),
            "pitch": kwargs.get("pitch", 1.0)
        }
        
        loop = asyncio.get_event_loop()
        
        # Make API request
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(
                f"{self.api_url}/synthesize",
                json=payload,
                timeout=30
            )
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Speaches TTS API failed: {response.text}")
        
        # Save audio data to file
        with open(output_file, 'wb') as f:
            f.write(response.content)
    
    def get_available_voices(self, language: Optional[str] = None) -> List[str]:
        """Get available voices for language"""
        if language is None:
            return self.supported_voices
        
        # Filter voices by language
        filtered_voices = [v for v in self.supported_voices if language in v.lower()]
        return filtered_voices if filtered_voices else self.supported_voices