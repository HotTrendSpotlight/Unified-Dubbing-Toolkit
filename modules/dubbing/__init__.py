"""
Dubbing Module
=============

This module provides high-level dubbing workflows and integrations.
"""

from .workflows import DubbingWorkflow
from .quality_control import QualityController
from .batch_processor import BatchProcessor

__all__ = [
    "DubbingWorkflow",
    "QualityController", 
    "BatchProcessor"
]