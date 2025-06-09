"""
High-level dubbing workflows
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..stt import get_available_models as get_stt_models
from ..tts import get_available_models as get_tts_models
from ..voice_cloning import get_available_models as get_vc_models
from ..lip_sync import get_available_models as get_ls_models


class DubbingWorkflow:
    """High-level dubbing workflow manager"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def auto_dub_workflow(self, input_file: str, output_file: str,
                               target_language: str, **kwargs) -> Dict[str, Any]:
        """
        Automatic dubbing workflow that selects best available models
        """
        self.logger.info(f"Starting auto-dub workflow: {input_file} -> {output_file}")
        
        # Select best available models
        stt_models = get_stt_models()
        tts_models = get_tts_models()
        
        # Prefer faster models for auto workflow
        stt_model = self._select_best_stt_model(stt_models)
        tts_model = self._select_best_tts_model(tts_models, target_language)
        
        self.logger.info(f"Selected models: STT={stt_model}, TTS={tts_model}")
        
        # Create and execute dubbing task
        from ...core import DubbingPipeline, DubbingTask
        
        pipeline = DubbingPipeline()
        task = DubbingTask(
            input_file=input_file,
            output_file=output_file,
            target_language=target_language,
            stt_model=stt_model,
            tts_model=tts_model,
            **kwargs
        )
        
        return await pipeline.process_task(task)
    
    def _select_best_stt_model(self, available_models: Dict) -> str:
        """Select the best available STT model"""
        # Preference order: faster_whisper > whisper > whisperx > whisper_cpp
        preferences = ["faster_whisper", "whisper", "whisperx", "whisper_cpp"]
        
        for model in preferences:
            if model in available_models and available_models[model].is_available():
                return model
        
        # Fallback to first available
        for model_name, model in available_models.items():
            if model.is_available():
                return model_name
        
        raise RuntimeError("No STT models available")
    
    def _select_best_tts_model(self, available_models: Dict, language: str) -> str:
        """Select the best available TTS model for the language"""
        # Preference order: bark > piper > kokoro > speaches
        preferences = ["bark", "piper", "kokoro", "speaches"]
        
        for model in preferences:
            if model in available_models:
                model_instance = available_models[model]
                if (model_instance.is_available() and 
                    language in model_instance.supported_languages):
                    return model
        
        # Fallback to first available that supports the language
        for model_name, model in available_models.items():
            if (model.is_available() and 
                language in model.supported_languages):
                return model_name
        
        # Last resort: any available model
        for model_name, model in available_models.items():
            if model.is_available():
                return model_name
        
        raise RuntimeError("No TTS models available")