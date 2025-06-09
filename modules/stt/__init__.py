"""
Speech-to-Text (STT) Module
===========================

This module provides interfaces to various STT engines including:
- OpenAI Whisper
- WhisperX  
- Faster Whisper
- Whisper.cpp
"""

from .base import STTBase
from .whisper_openai import WhisperOpenAI
from .whisper_x import WhisperX
from .faster_whisper import FasterWhisper
from .whisper_cpp import WhisperCpp

# Registry of available STT models
_MODELS = {}

def register_model(name: str, model_class):
    """Register an STT model"""
    _MODELS[name] = model_class

def get_available_models():
    """Get dictionary of available STT models"""
    models = {}
    
    # Try to load each model and register if available
    try:
        models['whisper'] = WhisperOpenAI()
        register_model('whisper', WhisperOpenAI)
    except ImportError:
        pass
    
    try:
        models['whisperx'] = WhisperX()
        register_model('whisperx', WhisperX)
    except ImportError:
        pass
    
    try:
        models['faster_whisper'] = FasterWhisper()
        register_model('faster_whisper', FasterWhisper)
    except ImportError:
        pass
    
    try:
        models['whisper_cpp'] = WhisperCpp()
        register_model('whisper_cpp', WhisperCpp)
    except ImportError:
        pass
    
    return models

def get_model(name: str):
    """Get a specific STT model by name"""
    if name not in _MODELS:
        raise ValueError(f"STT model '{name}' not available")
    return _MODELS[name]()

__all__ = [
    "STTBase",
    "WhisperOpenAI", 
    "WhisperX",
    "FasterWhisper",
    "WhisperCpp",
    "get_available_models",
    "get_model"
]