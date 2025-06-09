"""
Unified Dubbing System
=====================

A comprehensive, modular dubbing toolkit that integrates multiple speech-to-text,
text-to-speech, voice cloning, and lip sync technologies into a single unified pipeline.

Example usage:
    from unified_dubbing_system import DubbingPipeline, DubbingTask
    
    # Initialize pipeline
    pipeline = DubbingPipeline()
    
    # Create dubbing task
    task = DubbingTask(
        input_file="input.mp4",
        output_file="output.mp4",
        target_language="es"
    )
    
    # Process task
    result = await pipeline.process_task(task)
"""

__version__ = "1.0.0"
__author__ = "Unified Dubbing System Team"

from .core import DubbingPipeline, DubbingTask, ConfigManager
from .core.utils import AudioUtils, VideoUtils, setup_logging

__all__ = [
    "DubbingPipeline",
    "DubbingTask", 
    "ConfigManager",
    "AudioUtils",
    "VideoUtils",
    "setup_logging"
]