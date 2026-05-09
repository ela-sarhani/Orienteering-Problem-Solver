"""
Visualization package for Branch and Bound.
Provides state recording and interactive HTML viewer generation.
"""

from .state_recorder import StateRecorder, AlgorithmStep
from .viewer import generate_html_viewer

__all__ = ["StateRecorder", "AlgorithmStep", "generate_html_viewer"]
