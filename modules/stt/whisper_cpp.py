"""
Whisper.cpp STT Implementation
"""

import asyncio
import logging
import subprocess
import json
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path

from .base import STTBase


class WhisperCpp(STTBase):
    """Whisper.cpp implementation for fast CPU inference"""
    
    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        self.model_path = model_path
        self.name = "Whisper.cpp"
        self.description = "Whisper.cpp for fast CPU inference"
        self.supported_languages = [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", 
            "ar", "hi", "tr", "pl", "nl", "sv", "da", "no", "fi"
        ]
        self.requirements = ["whisper.cpp binary"]
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if whisper.cpp binary is available"""
        try:
            result = subprocess.run(
                ["whisper", "--help"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    async def transcribe(self, audio_file: str, language: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Transcribe audio using whisper.cpp"""
        if not self.is_available():
            raise RuntimeError("whisper.cpp not available. Please install whisper.cpp binary")
        
        if not self.validate_audio_file(audio_file):
            raise ValueError(f"Unsupported audio format: {Path(audio_file).suffix}")
        
        # Run transcription
        result = await self._transcribe_async(audio_file, language, kwargs)
        return self._format_result(result)
    
    async def _transcribe_async(self, audio_file: str, language: Optional[str], kwargs: Dict):
        """Run whisper.cpp transcription asynchronously"""
        # Create temporary output file for JSON results
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_file = tmp_file.name
        
        try:
            # Build command
            cmd = ["whisper", audio_file, "-oj", "-of", output_file.replace('.json', '')]
            
            # Add language if specified
            if language:
                cmd.extend(["-l", language])
            
            # Add model if specified
            if self.model_path:
                cmd.extend(["-m", self.model_path])
            
            # Add additional parameters
            for key, value in kwargs.items():
                if key == "threads":
                    cmd.extend(["-t", str(value)])
                elif key == "processors":
                    cmd.extend(["-p", str(value)])
            
            # Run command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"whisper.cpp failed: {stderr.decode()}")
            
            # Read JSON output
            with open(output_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            return result
            
        finally:
            # Clean up temporary file
            try:
                Path(output_file).unlink(missing_ok=True)
            except Exception:
                pass
    
    def _format_result(self, whisper_cpp_result: Dict) -> Dict[str, Any]:
        """Format whisper.cpp result to standard format"""
        transcription = whisper_cpp_result.get("transcription", [])
        
        segments = []
        full_text = ""
        
        for segment in transcription:
            text = segment.get("text", "").strip()
            segments.append({
                "start": segment.get("offsets", {}).get("from", 0) / 1000.0,  # Convert ms to seconds
                "end": segment.get("offsets", {}).get("to", 0) / 1000.0,
                "text": text,
                "confidence": segment.get("confidence", 0.0)
            })
            full_text += text + " "
        
        return {
            "text": full_text.strip(),
            "segments": segments,
            "language": whisper_cpp_result.get("language", "unknown"),
            "confidence": sum(s["confidence"] for s in segments) / len(segments) if segments else 0.0
        }