"""
Lip Sync Module
==============

This module provides interfaces to various lip sync systems including:
- Wav2Lip
"""

from .base import LipSyncBase
from .wav2lip import Wav2Lip

# Registry of available lip sync models
_MODELS = {}

def register_model(name: str, model_class):
    """Register a lip sync model"""
    _MODELS[name] = model_class

def get_available_models():
    """Get dictionary of available lip sync models"""
    models = {}
    
    # Try to load each model and register if available
    try:
        models['wav2lip'] = Wav2Lip()
        register_model('wav2lip', Wav2Lip)
    except ImportError:
        pass
    
    return models

def get_model(name: str):
    """Get a specific lip sync model by name"""
    if name not in _MODELS:
        raise ValueError(f"Lip sync model '{name}' not available")
    return _MODELS[name]()

__all__ = [
    "LipSyncBase",
    "Wav2Lip",
    "get_available_models",
    "get_model"
]