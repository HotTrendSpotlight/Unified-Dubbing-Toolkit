"""
Base class for Text-to-Speech modules
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import asyncio


class TTSBase(ABC):
    """Base class for all TTS implementations"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "Base TTS implementation"
        self.supported_languages = []
        self.supported_voices = []
        self.quality_levels = ["low", "medium", "high"]
        self.requirements = []
    
    @abstractmethod
    async def synthesize(self, text: Union[str, Dict], output_file: str, 
                        language: str = "en", voice: Optional[str] = None,
                        quality: str = "medium", **kwargs) -> str:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize (string or transcript dict with segments)
            output_file: Path to output audio file
            language: Language code
            voice: Voice identifier (optional)
            quality: Quality level (low, medium, high)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Path to generated audio file
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the TTS model is available and properly configured"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this TTS model"""
        return {
            "name": self.name,
            "description": self.description,
            "supported_languages": self.supported_languages,
            "supported_voices": self.supported_voices,
            "quality_levels": self.quality_levels,
            "requirements": self.requirements,
            "available": self.is_available()
        }
    
    async def synthesize_segments(self, segments: List[Dict], output_file: str,
                                language: str = "en", voice: Optional[str] = None,
                                quality: str = "medium", **kwargs) -> str:
        """
        Synthesize speech from transcript segments with timing
        
        Args:
            segments: List of segment dicts with 'text', 'start', 'end'
            output_file: Path to output audio file
            language: Language code
            voice: Voice identifier
            quality: Quality level
            **kwargs: Additional parameters
            
        Returns:
            Path to generated audio file
        """
        # Default implementation: concatenate all text and synthesize
        full_text = " ".join(segment.get("text", "") for segment in segments)
        return await self.synthesize(full_text, output_file, language, voice, quality, **kwargs)
    
    def get_available_voices(self, language: Optional[str] = None) -> List[str]:
        """Get list of available voices, optionally filtered by language"""
        if language is None:
            return self.supported_voices
        
        # Default implementation returns all voices
        # Subclasses should override to filter by language
        return self.supported_voices
    
    def validate_language(self, language: str) -> bool:
        """Validate if language is supported"""
        return language in self.supported_languages
    
    def validate_voice(self, voice: str, language: Optional[str] = None) -> bool:
        """Validate if voice is supported for the given language"""
        available_voices = self.get_available_voices(language)
        return voice in available_voices