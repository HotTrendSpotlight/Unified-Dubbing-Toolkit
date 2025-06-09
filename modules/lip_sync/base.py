"""
Base class for Lip Sync modules
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio


class LipSyncBase(ABC):
    """Base class for all lip sync implementations"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "Base lip sync implementation"
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv']
        self.supported_audio_formats = ['.wav', '.mp3', '.flac']
        self.requirements = []
        self.quality_levels = ["low", "medium", "high"]
    
    @abstractmethod
    async def sync_lips(self, video_file: str, audio_file: str, 
                       output_file: str, **kwargs) -> str:
        """
        Synchronize lips in video with provided audio
        
        Args:
            video_file: Path to input video file
            audio_file: Path to audio file to sync with
            output_file: Path to output video file
            **kwargs: Additional model-specific parameters
            
        Returns:
            Path to generated video file with synced lips
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the lip sync model is available and properly configured"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this lip sync model"""
        return {
            "name": self.name,
            "description": self.description,
            "supported_video_formats": self.supported_video_formats,
            "supported_audio_formats": self.supported_audio_formats,
            "quality_levels": self.quality_levels,
            "requirements": self.requirements,
            "available": self.is_available()
        }
    
    def validate_video_file(self, video_file: str) -> bool:
        """Validate if video file is supported"""
        from pathlib import Path
        return Path(video_file).suffix.lower() in self.supported_video_formats
    
    def validate_audio_file(self, audio_file: str) -> bool:
        """Validate if audio file is supported"""
        from pathlib import Path
        return Path(audio_file).suffix.lower() in self.supported_audio_formats
    
    async def preprocess_video(self, video_file: str, target_fps: int = 25) -> str:
        """
        Preprocess video file if needed
        Default implementation returns the original file
        """
        return video_file
    
    async def preprocess_audio(self, audio_file: str, target_sample_rate: int = 16000) -> str:
        """
        Preprocess audio file if needed
        Default implementation returns the original file
        """
        return audio_file
    
    def get_quality_settings(self, quality: str) -> Dict[str, Any]:
        """Get quality-specific settings"""
        quality_map = {
            "low": {
                "resolution": "480p",
                "fps": 24,
                "bitrate": "1M"
            },
            "medium": {
                "resolution": "720p", 
                "fps": 25,
                "bitrate": "2M"
            },
            "high": {
                "resolution": "1080p",
                "fps": 30,
                "bitrate": "4M"
            }
        }
        
        return quality_map.get(quality, quality_map["medium"])