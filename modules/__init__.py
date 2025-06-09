"""
Unified Dubbing System - Modules Package
========================================

This package contains all the specialized modules for different aspects
of the dubbing pipeline: STT, TTS, Voice Cloning, Lip Sync, and Dubbing.
"""

from . import stt, tts, voice_cloning, lip_sync, dubbing

__all__ = ["stt", "tts", "voice_cloning", "lip_sync", "dubbing"]