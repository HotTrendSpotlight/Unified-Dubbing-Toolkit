"""
Base class for Speech-to-Text modules
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio


class STTBase(ABC):
    """Base class for all STT implementations"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "Base STT implementation"
        self.supported_languages = []
        self.supported_formats = ['.wav', '.mp3', '.flac']
        self.requirements = []
    
    @abstractmethod
    async def transcribe(self, audio_file: str, language: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file: Path to audio file
            language: Language code (optional, auto-detect if None)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict containing:
            - text: Full transcribed text
            - segments: List of segments with timestamps
            - language: Detected/specified language
            - confidence: Overall confidence score
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the STT model is available and properly configured"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this STT model"""
        return {
            "name": self.name,
            "description": self.description,
            "supported_languages": self.supported_languages,
            "supported_formats": self.supported_formats,
            "requirements": self.requirements,
            "available": self.is_available()
        }
    
    async def preprocess_audio(self, audio_file: str) -> str:
        """
        Preprocess audio file if needed
        Default implementation returns the original file
        """
        return audio_file
    
    def validate_audio_file(self, audio_file: str) -> bool:
        """Validate if audio file is supported"""
        from pathlib import Path
        return Path(audio_file).suffix.lower() in self.supported_formats