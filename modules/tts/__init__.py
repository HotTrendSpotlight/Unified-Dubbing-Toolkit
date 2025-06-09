"""
Text-to-Speech (TTS) Module
===========================

This module provides interfaces to various TTS engines including:
- Bark TTS
- Piper TTS
- Kokoro TTS
- Speaches TTS
"""

from .base import TTSBase
from .bark_tts import BarkTTS
from .piper_tts import PiperTTS
from .kokoro_tts import KokoroTTS
from .speaches_tts import SpeachesTTS

# Registry of available TTS models
_MODELS = {}

def register_model(name: str, model_class):
    """Register a TTS model"""
    _MODELS[name] = model_class

def get_available_models():
    """Get dictionary of available TTS models"""
    models = {}
    
    # Try to load each model and register if available
    try:
        models['bark'] = BarkTTS()
        register_model('bark', BarkTTS)
    except ImportError:
        pass
    
    try:
        models['piper'] = PiperTTS()
        register_model('piper', PiperTTS)
    except ImportError:
        pass
    
    try:
        models['kokoro'] = KokoroTTS()
        register_model('kokoro', KokoroTTS)
    except ImportError:
        pass
    
    try:
        models['speaches'] = SpeachesTTS()
        register_model('speaches', SpeachesTTS)
    except ImportError:
        pass
    
    return models

def get_model(name: str):
    """Get a specific TTS model by name"""
    if name not in _MODELS:
        raise ValueError(f"TTS model '{name}' not available")
    return _MODELS[name]()

__all__ = [
    "TTSBase",
    "BarkTTS",
    "PiperTTS", 
    "KokoroTTS",
    "SpeachesTTS",
    "get_available_models",
    "get_model"
]