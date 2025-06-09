"""
Wav2Lip Implementation
"""

import asyncio
import logging
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
from pathlib import Path

from .base import LipSyncBase


class Wav2Lip(LipSyncBase):
    """Wav2Lip lip sync implementation"""
    
    def __init__(self, checkpoint_path: Optional[str] = None):
        super().__init__()
        self.checkpoint_path = checkpoint_path or "checkpoints/wav2lip_gan.pth"
        self.name = "Wav2Lip"
        self.description = "Wav2Lip: Accurately Lip-sync Videos In The Wild"
        self.requirements = ["torch", "torchvision", "opencv-python", "librosa", "scipy", "tqdm"]
        self.quality_levels = ["medium", "high"]  # Wav2Lip doesn't have low quality
        self.logger = logging.getLogger(__name__)
        
        # Wav2Lip script path (assuming it's in the repository)
        self.wav2lip_script = None
        self._find_wav2lip_script()
    
    def _find_wav2lip_script(self):
        """Find Wav2Lip inference script"""
        # Look for inference.py in common locations
        possible_paths = [
            "Wav2Lip-master/inference.py",
            "../Wav2Lip-master/inference.py", 
            "inference.py"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                self.wav2lip_script = str(Path(path).absolute())
                break
    
    def is_available(self) -> bool:
        """Check if Wav2Lip is available"""
        try:
            # Check if required packages are available
            import torch
            import cv2
            import librosa
            
            # Check if inference script exists
            if not self.wav2lip_script or not Path(self.wav2lip_script).exists():
                return False
            
            # Check if checkpoint exists
            return Path(self.checkpoint_path).exists()
            
        except ImportError:
            return False
    
    async def sync_lips(self, video_file: str, audio_file: str, 
                       output_file: str, **kwargs) -> str:
        """Synchronize lips using Wav2Lip"""
        if not self.is_available():
            raise RuntimeError("Wav2Lip not available. Check dependencies and model files")
        
        if not self.validate_video_file(video_file):
            raise ValueError(f"Unsupported video format: {Path(video_file).suffix}")
        
        if not self.validate_audio_file(audio_file):
            raise ValueError(f"Unsupported audio format: {Path(audio_file).suffix}")
        
        # Preprocess files if needed
        processed_video = await self.preprocess_video(video_file)
        processed_audio = await self.preprocess_audio(audio_file)
        
        # Run Wav2Lip inference
        await self._run_wav2lip(processed_video, processed_audio, output_file, kwargs)
        
        return output_file
    
    async def _run_wav2lip(self, video_file: str, audio_file: str, 
                          output_file: str, kwargs: Dict):
        """Run Wav2Lip inference script"""
        # Build command
        cmd = [
            "python", self.wav2lip_script,
            "--checkpoint_path", self.checkpoint_path,
            "--face", video_file,
            "--audio", audio_file,
            "--outfile", output_file
        ]
        
        # Add optional parameters
        if "face_det_batch_size" in kwargs:
            cmd.extend(["--face_det_batch_size", str(kwargs["face_det_batch_size"])])
        
        if "wav2lip_batch_size" in kwargs:
            cmd.extend(["--wav2lip_batch_size", str(kwargs["wav2lip_batch_size"])])
        
        if "resize_factor" in kwargs:
            cmd.extend(["--resize_factor", str(kwargs["resize_factor"])])
        
        if "crop" in kwargs:
            crop = kwargs["crop"]
            cmd.extend(["--crop", f"{crop[0]},{crop[1]},{crop[2]},{crop[3]}"])
        
        if "box" in kwargs:
            box = kwargs["box"]
            cmd.extend(["--box", f"{box[0]},{box[1]},{box[2]},{box[3]}"])
        
        if kwargs.get("rotate", False):
            cmd.append("--rotate")
        
        if kwargs.get("nosmooth", False):
            cmd.append("--nosmooth")
        
        # Set quality-specific parameters
        quality = kwargs.get("quality", "medium")
        quality_settings = self.get_quality_settings(quality)
        
        if "pads" not in kwargs:
            # Default padding based on quality
            if quality == "high":
                cmd.extend(["--pads", "0,10,0,0"])
            else:
                cmd.extend(["--pads", "0,15,0,0"])
        else:
            pads = kwargs["pads"]
            cmd.extend(["--pads", f"{pads[0]},{pads[1]},{pads[2]},{pads[3]}"])
        
        # Run command
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path(self.wav2lip_script).parent
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Wav2Lip failed: {error_msg}")
            
            self.logger.info("Wav2Lip processing completed successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to run Wav2Lip: {str(e)}")
    
    async def preprocess_video(self, video_file: str, target_fps: int = 25) -> str:
        """Preprocess video for Wav2Lip"""
        # Wav2Lip works best with specific video properties
        # This could include face detection, cropping, etc.
        
        # For now, return original file
        # In a full implementation, you might:
        # 1. Detect and crop faces
        # 2. Resize to optimal resolution
        # 3. Adjust frame rate
        
        return video_file
    
    async def preprocess_audio(self, audio_file: str, target_sample_rate: int = 16000) -> str:
        """Preprocess audio for Wav2Lip"""
        # Wav2Lip expects 16kHz audio
        if not audio_file.endswith('.wav'):
            # Convert to WAV if needed
            temp_wav = tempfile.mktemp(suffix='.wav')
            
            cmd = [
                'ffmpeg', '-i', audio_file,
                '-ar', str(target_sample_rate),
                '-ac', '1',
                '-y', temp_wav
            ]
            
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.communicate()
                
                if process.returncode == 0:
                    return temp_wav
                else:
                    # If conversion fails, return original
                    return audio_file
                    
            except Exception:
                return audio_file
        
        return audio_file
    
    def get_quality_settings(self, quality: str) -> Dict[str, Any]:
        """Get Wav2Lip-specific quality settings"""
        quality_map = {
            "medium": {
                "face_det_batch_size": 16,
                "wav2lip_batch_size": 128,
                "resize_factor": 1,
                "pads": [0, 15, 0, 0]
            },
            "high": {
                "face_det_batch_size": 8,
                "wav2lip_batch_size": 64,
                "resize_factor": 1,
                "pads": [0, 10, 0, 0]
            }
        }
        
        return quality_map.get(quality, quality_map["medium"])