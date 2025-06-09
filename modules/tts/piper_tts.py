"""
Piper TTS Implementation
"""

import asyncio
import logging
import subprocess
import tempfile
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from .base import TTSBase


class PiperTTS(TTSBase):
    """Piper TTS implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = "Piper TTS"
        self.description = "Fast, local neural text to speech system"
        self.supported_languages = [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", 
            "ar", "hi", "tr", "pl", "nl", "sv", "da", "no", "fi"
        ]
        self.supported_voices = [
            "en_US-lessac-medium", "en_US-lessac-low", "en_US-lessac-high",
            "en_US-ryan-medium", "en_US-ryan-low", "en_US-ryan-high",
            "en_GB-alan-medium", "en_GB-alan-low",
            "es_ES-mls_10246-low", "es_ES-mls_9972-low",
            "fr_FR-mls_1840-low", "fr_FR-upmc-medium",
            "de_DE-thorsten-medium", "de_DE-thorsten-low"
        ]
        self.quality_levels = ["low", "medium", "high"]
        self.requirements = ["piper-tts"]
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if Piper is available"""
        try:
            result = subprocess.run(
                ["piper", "--help"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    async def synthesize(self, text: Union[str, Dict], output_file: str, 
                        language: str = "en", voice: Optional[str] = None,
                        quality: str = "medium", **kwargs) -> str:
        """Synthesize speech using Piper TTS"""
        if not self.is_available():
            raise RuntimeError("Piper TTS not available. Install piper-tts")
        
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
        
        # Select voice based on language and quality
        if voice is None:
            voice = self._select_voice(language, quality)
        
        # Run synthesis
        await self._synthesize_async(text, voice, output_file, kwargs)
        
        return output_file
    
    def _select_voice(self, language: str, quality: str) -> str:
        """Select appropriate voice for language and quality"""
        voice_map = {
            "en": {
                "low": "en_US-lessac-low",
                "medium": "en_US-lessac-medium", 
                "high": "en_US-lessac-high"
            },
            "es": {
                "low": "es_ES-mls_10246-low",
                "medium": "es_ES-mls_10246-low",
                "high": "es_ES-mls_10246-low"
            },
            "fr": {
                "low": "fr_FR-mls_1840-low",
                "medium": "fr_FR-upmc-medium",
                "high": "fr_FR-upmc-medium"
            },
            "de": {
                "low": "de_DE-thorsten-low",
                "medium": "de_DE-thorsten-medium",
                "high": "de_DE-thorsten-medium"
            }
        }
        
        if language in voice_map and quality in voice_map[language]:
            return voice_map[language][quality]
        
        # Default fallback
        return "en_US-lessac-medium"
    
    async def _synthesize_async(self, text: str, voice: str, output_file: str, kwargs: Dict):
        """Run Piper synthesis asynchronously"""
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(text)
            text_file = tmp_file.name
        
        try:
            # Build command
            cmd = [
                "piper",
                "--model", voice,
                "--output_file", output_file
            ]
            
            # Add additional parameters
            if "speaker" in kwargs:
                cmd.extend(["--speaker", str(kwargs["speaker"])])
            
            if "length_scale" in kwargs:
                cmd.extend(["--length_scale", str(kwargs["length_scale"])])
            
            if "noise_scale" in kwargs:
                cmd.extend(["--noise_scale", str(kwargs["noise_scale"])])
            
            # Run command with text input
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=text.encode('utf-8'))
            
            if process.returncode != 0:
                raise RuntimeError(f"Piper TTS failed: {stderr.decode()}")
                
        finally:
            # Clean up temporary file
            try:
                Path(text_file).unlink(missing_ok=True)
            except Exception:
                pass
    
    def get_available_voices(self, language: Optional[str] = None) -> List[str]:
        """Get available voices for language"""
        if language is None:
            return self.supported_voices
        
        # Filter voices by language
        filtered_voices = []
        for voice in self.supported_voices:
            if voice.startswith(f"{language}_"):
                filtered_voices.append(voice)
        
        return filtered_voices if filtered_voices else ["en_US-lessac-medium"]