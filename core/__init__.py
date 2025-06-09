"""
Unified Dubbing System - Core Module
====================================

This module provides the core functionality for the unified dubbing system,
including pipeline orchestration, utilities, and base classes.
"""

__version__ = "1.0.0"
__author__ = "Unified Dubbing System Team"

from .pipeline import DubbingPipeline, DubbingTask
from .utils import AudioUtils, VideoUtils, ConfigManager, setup_logging

__all__ = [
    "DubbingPipeline",
    "DubbingTask",
    "AudioUtils", 
    "VideoUtils",
    "ConfigManager",
    "setup_logging"
]