"""
Base class for Voice Cloning modules
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio


class VoiceCloningBase(ABC):
    """Base class for all voice cloning implementations"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "Base voice cloning implementation"
        self.supported_languages = []
        self.supported_formats = ['.wav', '.mp3', '.flac']
        self.requirements = []
        self.min_reference_duration = 5.0  # Minimum seconds of reference audio
        self.max_reference_duration = 300.0  # Maximum seconds of reference audio
    
    @abstractmethod
    async def clone_voice(self, source_audio: str, reference_audio: str, 
                         output_file: str, **kwargs) -> str:
        """
        Clone voice from reference audio and apply to source audio
        
        Args:
            source_audio: Path to source audio to be converted
            reference_audio: Path to reference audio with target voice
            output_file: Path to output audio file
            **kwargs: Additional model-specific parameters
            
        Returns:
            Path to generated audio file with cloned voice
        """
        pass
    
    @abstractmethod
    async def train_voice_model(self, reference_audios: List[str], 
                               voice_name: str, **kwargs) -> str:
        """
        Train a voice model from reference audio files
        
        Args:
            reference_audios: List of paths to reference audio files
            voice_name: Name for the trained voice model
            **kwargs: Additional training parameters
            
        Returns:
            Path or identifier for the trained voice model
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the voice cloning model is available and properly configured"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this voice cloning model"""
        return {
            "name": self.name,
            "description": self.description,
            "supported_languages": self.supported_languages,
            "supported_formats": self.supported_formats,
            "requirements": self.requirements,
            "min_reference_duration": self.min_reference_duration,
            "max_reference_duration": self.max_reference_duration,
            "available": self.is_available()
        }
    
    def validate_audio_file(self, audio_file: str) -> bool:
        """Validate if audio file is supported"""
        from pathlib import Path
        return Path(audio_file).suffix.lower() in self.supported_formats
    
    async def validate_reference_audio(self, reference_audio: str) -> bool:
        """Validate reference audio duration and quality"""
        if not self.validate_audio_file(reference_audio):
            return False
        
        # Check duration (this would need audio utils)
        try:
            from ...core.utils import AudioUtils
            audio_utils = AudioUtils()
            duration = await audio_utils.get_audio_duration(reference_audio)
            
            return (self.min_reference_duration <= duration <= self.max_reference_duration)
        except Exception:
            # If we can't check duration, assume it's valid
            return True
    
    async def preprocess_audio(self, audio_file: str, target_sample_rate: int = 22050) -> str:
        """
        Preprocess audio file for voice cloning
        Default implementation returns the original file
        """
        return audio_file
    
    def get_supported_voice_models(self) -> List[str]:
        """Get list of pre-trained voice models available"""
        return []  # Override in subclasses