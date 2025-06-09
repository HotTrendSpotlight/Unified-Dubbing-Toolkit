"""
Main Pipeline Orchestrator for the Unified Dubbing System
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio

from .utils import AudioUtils, VideoUtils, ConfigManager


@dataclass
class DubbingTask:
    """Represents a dubbing task with all necessary parameters"""
    input_file: str
    output_file: str
    target_language: str
    source_language: Optional[str] = None
    voice_model: Optional[str] = None
    stt_model: str = "whisper"
    tts_model: str = "bark"
    lip_sync: bool = True
    quality: str = "medium"  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_file": self.input_file,
            "output_file": self.output_file,
            "target_language": self.target_language,
            "source_language": self.source_language,
            "voice_model": self.voice_model,
            "stt_model": self.stt_model,
            "tts_model": self.tts_model,
            "lip_sync": self.lip_sync,
            "quality": self.quality
        }


class DubbingPipeline:
    """
    Main orchestrator for the dubbing pipeline.
    Coordinates between STT, TTS, Voice Cloning, and Lip Sync modules.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = ConfigManager(config_path)
        self.logger = logging.getLogger(__name__)
        self.audio_utils = AudioUtils()
        self.video_utils = VideoUtils()
        
        # Module registry - will be populated by module loaders
        self.modules = {
            'stt': {},
            'tts': {},
            'voice_cloning': {},
            'lip_sync': {},
            'dubbing': {}
        }
        
        self._load_modules()
    
    def _load_modules(self):
        """Load available modules based on configuration"""
        try:
            # Import modules dynamically based on availability
            from ..modules.stt import get_available_models as get_stt_models
            from ..modules.tts import get_available_models as get_tts_models
            from ..modules.voice_cloning import get_available_models as get_vc_models
            from ..modules.lip_sync import get_available_models as get_ls_models
            
            self.modules['stt'] = get_stt_models()
            self.modules['tts'] = get_tts_models()
            self.modules['voice_cloning'] = get_vc_models()
            self.modules['lip_sync'] = get_ls_models()
            
            self.logger.info(f"Loaded modules: {list(self.modules.keys())}")
            
        except ImportError as e:
            self.logger.warning(f"Some modules could not be loaded: {e}")
    
    async def process_task(self, task: DubbingTask) -> Dict[str, Any]:
        """
        Process a complete dubbing task
        
        Args:
            task: DubbingTask object containing all parameters
            
        Returns:
            Dict containing results and metadata
        """
        self.logger.info(f"Starting dubbing task: {task.input_file} -> {task.output_file}")
        
        results = {
            "task": task.to_dict(),
            "status": "processing",
            "steps": {},
            "intermediate_files": [],
            "metrics": {}
        }
        
        try:
            # Step 1: Extract audio from video if needed
            audio_file = await self._extract_audio(task.input_file, results)
            
            # Step 2: Speech-to-Text transcription
            transcript = await self._transcribe_audio(audio_file, task, results)
            
            # Step 3: Translate transcript if needed
            if task.target_language != task.source_language:
                transcript = await self._translate_transcript(transcript, task, results)
            
            # Step 4: Text-to-Speech synthesis
            dubbed_audio = await self._synthesize_speech(transcript, task, results)
            
            # Step 5: Voice cloning if specified
            if task.voice_model:
                dubbed_audio = await self._clone_voice(dubbed_audio, task, results)
            
            # Step 6: Lip sync if video input
            if task.lip_sync and self.video_utils.is_video_file(task.input_file):
                final_output = await self._apply_lip_sync(
                    task.input_file, dubbed_audio, task.output_file, results
                )
            else:
                # Just replace audio track
                final_output = await self._replace_audio_track(
                    task.input_file, dubbed_audio, task.output_file, results
                )
            
            results["status"] = "completed"
            results["output_file"] = final_output
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    async def _extract_audio(self, input_file: str, results: Dict) -> str:
        """Extract audio from video file"""
        if self.audio_utils.is_audio_file(input_file):
            return input_file
        
        audio_file = f"{Path(input_file).stem}_extracted.wav"
        await self.video_utils.extract_audio(input_file, audio_file)
        
        results["steps"]["audio_extraction"] = {
            "status": "completed",
            "output": audio_file
        }
        results["intermediate_files"].append(audio_file)
        
        return audio_file
    
    async def _transcribe_audio(self, audio_file: str, task: DubbingTask, results: Dict) -> Dict:
        """Transcribe audio to text using specified STT model"""
        stt_module = self.modules['stt'].get(task.stt_model)
        if not stt_module:
            raise ValueError(f"STT model '{task.stt_model}' not available")
        
        transcript = await stt_module.transcribe(
            audio_file, 
            language=task.source_language
        )
        
        results["steps"]["transcription"] = {
            "status": "completed",
            "model": task.stt_model,
            "transcript": transcript
        }
        
        return transcript
    
    async def _translate_transcript(self, transcript: Dict, task: DubbingTask, results: Dict) -> Dict:
        """Translate transcript to target language"""
        # This would integrate with translation services
        # For now, return as-is
        results["steps"]["translation"] = {
            "status": "skipped",
            "reason": "Translation module not implemented"
        }
        return transcript
    
    async def _synthesize_speech(self, transcript: Dict, task: DubbingTask, results: Dict) -> str:
        """Synthesize speech from transcript using specified TTS model"""
        tts_module = self.modules['tts'].get(task.tts_model)
        if not tts_module:
            raise ValueError(f"TTS model '{task.tts_model}' not available")
        
        output_audio = f"{Path(task.output_file).stem}_tts.wav"
        await tts_module.synthesize(
            transcript,
            output_audio,
            language=task.target_language,
            quality=task.quality
        )
        
        results["steps"]["tts"] = {
            "status": "completed",
            "model": task.tts_model,
            "output": output_audio
        }
        results["intermediate_files"].append(output_audio)
        
        return output_audio
    
    async def _clone_voice(self, audio_file: str, task: DubbingTask, results: Dict) -> str:
        """Apply voice cloning to synthesized audio"""
        vc_module = self.modules['voice_cloning'].get('default')
        if not vc_module:
            self.logger.warning("Voice cloning module not available, skipping")
            return audio_file
        
        cloned_audio = f"{Path(audio_file).stem}_cloned.wav"
        await vc_module.clone_voice(
            audio_file,
            task.voice_model,
            cloned_audio
        )
        
        results["steps"]["voice_cloning"] = {
            "status": "completed",
            "model": task.voice_model,
            "output": cloned_audio
        }
        results["intermediate_files"].append(cloned_audio)
        
        return cloned_audio
    
    async def _apply_lip_sync(self, video_file: str, audio_file: str, output_file: str, results: Dict) -> str:
        """Apply lip sync to video with new audio"""
        ls_module = self.modules['lip_sync'].get('wav2lip')
        if not ls_module:
            # Fallback to simple audio replacement
            return await self._replace_audio_track(video_file, audio_file, output_file, results)
        
        await ls_module.sync_lips(video_file, audio_file, output_file)
        
        results["steps"]["lip_sync"] = {
            "status": "completed",
            "model": "wav2lip",
            "output": output_file
        }
        
        return output_file
    
    async def _replace_audio_track(self, video_file: str, audio_file: str, output_file: str, results: Dict) -> str:
        """Replace audio track in video file"""
        await self.video_utils.replace_audio(video_file, audio_file, output_file)
        
        results["steps"]["audio_replacement"] = {
            "status": "completed",
            "output": output_file
        }
        
        return output_file
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models for each module type"""
        return {
            module_type: list(models.keys()) 
            for module_type, models in self.modules.items()
        }
    
    def get_module_info(self, module_type: str, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific module"""
        if module_type not in self.modules:
            raise ValueError(f"Unknown module type: {module_type}")
        
        if model_name not in self.modules[module_type]:
            raise ValueError(f"Unknown model: {model_name}")
        
        module = self.modules[module_type][model_name]
        return {
            "name": model_name,
            "type": module_type,
            "description": getattr(module, 'description', 'No description available'),
            "supported_languages": getattr(module, 'supported_languages', []),
            "quality_levels": getattr(module, 'quality_levels', ['medium']),
            "requirements": getattr(module, 'requirements', [])
        }