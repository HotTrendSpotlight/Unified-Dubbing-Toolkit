"""
Command Line Interface for Unified Dubbing System
"""

from .main import main_cli
from .commands import DubbingCommands

__all__ = ["main_cli", "DubbingCommands"]