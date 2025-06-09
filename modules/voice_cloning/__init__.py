"""
Voice Cloning Module
===================

This module provides interfaces to various voice cloning systems including:
- Real-Time Voice Cloning
- AllVoiceLab
- Misaki
"""

from .base import VoiceCloningBase
from .real_time_vc import RealTimeVoiceCloning
from .allvoicelab import AllVoiceLab
from .misaki_vc import MisakiVC

# Registry of available voice cloning models
_MODELS = {}

def register_model(name: str, model_class):
    """Register a voice cloning model"""
    _MODELS[name] = model_class

def get_available_models():
    """Get dictionary of available voice cloning models"""
    models = {}
    
    # Try to load each model and register if available
    try:
        models['real_time_vc'] = RealTimeVoiceCloning()
        register_model('real_time_vc', RealTimeVoiceCloning)
    except ImportError:
        pass
    
    try:
        models['allvoicelab'] = AllVoiceLab()
        register_model('allvoicelab', AllVoiceLab)
    except ImportError:
        pass
    
    try:
        models['misaki'] = MisakiVC()
        register_model('misaki', MisakiVC)
    except ImportError:
        pass
    
    return models

def get_model(name: str):
    """Get a specific voice cloning model by name"""
    if name not in _MODELS:
        raise ValueError(f"Voice cloning model '{name}' not available")
    return _MODELS[name]()

__all__ = [
    "VoiceCloningBase",
    "RealTimeVoiceCloning",
    "AllVoiceLab", 
    "MisakiVC",
    "get_available_models",
    "get_model"
]