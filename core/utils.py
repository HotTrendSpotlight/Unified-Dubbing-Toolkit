"""
Utility classes and functions for the Unified Dubbing System
"""

import json
import yaml
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import tempfile
import shutil


class ConfigManager:
    """Manages configuration for the dubbing system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/config.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            return self._get_default_config()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    return yaml.safe_load(f)
        except Exception as e:
            logging.warning(f"Failed to load config from {config_file}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "audio": {
                "sample_rate": 16000,
                "format": "wav",
                "channels": 1
            },
            "video": {
                "fps": 25,
                "codec": "libx264",
                "quality": "medium"
            },
            "models": {
                "stt": {
                    "default": "whisper",
                    "whisper": {
                        "model_size": "base",
                        "language": "auto"
                    },
                    "faster_whisper": {
                        "model_size": "base",
                        "compute_type": "float16"
                    }
                },
                "tts": {
                    "default": "bark",
                    "bark": {
                        "voice_preset": "v2/en_speaker_6"
                    },
                    "piper": {
                        "model": "en_US-lessac-medium"
                    }
                },
                "voice_cloning": {
                    "default": "real_time_vc",
                    "real_time_vc": {
                        "encoder_model": "encoder.pt",
                        "synthesizer_model": "synthesizer.pt",
                        "vocoder_model": "vocoder.pt"
                    }
                },
                "lip_sync": {
                    "default": "wav2lip",
                    "wav2lip": {
                        "checkpoint": "wav2lip_gan.pth",
                        "face_detect": "s3fd"
                    }
                }
            },
            "paths": {
                "models": "models/",
                "temp": "temp/",
                "output": "output/"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file"""
        save_path = Path(path or self.config_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            if save_path.suffix.lower() == '.json':
                json.dump(self.config, f, indent=2)
            else:
                yaml.dump(self.config, f, default_flow_style=False)


class AudioUtils:
    """Utilities for audio processing"""
    
    AUDIO_EXTENSIONS = {'.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a'}
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def is_audio_file(self, file_path: str) -> bool:
        """Check if file is an audio file"""
        return Path(file_path).suffix.lower() in self.AUDIO_EXTENSIONS
    
    async def convert_audio(self, input_file: str, output_file: str, 
                          sample_rate: int = 16000, channels: int = 1) -> None:
        """Convert audio file to specified format"""
        cmd = [
            'ffmpeg', '-i', input_file,
            '-ar', str(sample_rate),
            '-ac', str(channels),
            '-y', output_file
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")
                
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
    
    async def get_audio_duration(self, file_path: str) -> float:
        """Get duration of audio file in seconds"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', file_path
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"FFprobe failed: {stderr.decode()}")
            
            return float(stdout.decode().strip())
            
        except (FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"Failed to get audio duration: {e}")
    
    async def extract_audio_segment(self, input_file: str, output_file: str,
                                  start_time: float, duration: float) -> None:
        """Extract a segment from audio file"""
        cmd = [
            'ffmpeg', '-i', input_file,
            '-ss', str(start_time),
            '-t', str(duration),
            '-y', output_file
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError("Failed to extract audio segment")
                
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")


class VideoUtils:
    """Utilities for video processing"""
    
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def is_video_file(self, file_path: str) -> bool:
        """Check if file is a video file"""
        return Path(file_path).suffix.lower() in self.VIDEO_EXTENSIONS
    
    async def extract_audio(self, video_file: str, audio_file: str) -> None:
        """Extract audio from video file"""
        cmd = [
            'ffmpeg', '-i', video_file,
            '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1',
            '-y', audio_file
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"Failed to extract audio: {stderr.decode()}")
                
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
    
    async def replace_audio(self, video_file: str, audio_file: str, output_file: str) -> None:
        """Replace audio track in video file"""
        cmd = [
            'ffmpeg', '-i', video_file, '-i', audio_file,
            '-c:v', 'copy', '-c:a', 'aac',
            '-map', '0:v:0', '-map', '1:a:0',
            '-y', output_file
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"Failed to replace audio: {stderr.decode()}")
                
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
    
    async def get_video_info(self, video_file: str) -> Dict[str, Any]:
        """Get video file information"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_file
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"FFprobe failed: {stderr.decode()}")
            
            return json.loads(stdout.decode())
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to get video info: {e}")


class FileManager:
    """Manages temporary and output files"""
    
    def __init__(self, temp_dir: Optional[str] = None, output_dir: Optional[str] = None):
        self.temp_dir = Path(temp_dir or tempfile.gettempdir()) / "unified_dubbing"
        self.output_dir = Path(output_dir or "output")
        
        # Create directories
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.temp_files: List[Path] = []
    
    def get_temp_file(self, suffix: str = "", prefix: str = "temp_") -> str:
        """Get a temporary file path"""
        temp_file = self.temp_dir / f"{prefix}{len(self.temp_files)}{suffix}"
        self.temp_files.append(temp_file)
        return str(temp_file)
    
    def get_output_file(self, filename: str) -> str:
        """Get an output file path"""
        return str(self.output_dir / filename)
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception as e:
                logging.warning(f"Failed to delete temp file {temp_file}: {e}")
        
        self.temp_files.clear()
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup_temp_files()


def setup_logging(level: str = "INFO", format_str: Optional[str] = None) -> None:
    """Setup logging configuration"""
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("dubbing_system.log")
        ]
    )


def validate_file_path(file_path: str, must_exist: bool = True) -> Path:
    """Validate and return Path object for file"""
    path = Path(file_path)
    
    if must_exist and not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return path


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return Path(file_path).stat().st_size


def ensure_directory(dir_path: str) -> Path:
    """Ensure directory exists and return Path object"""
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path