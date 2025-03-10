"""CLI module for RichCLI"""

from .base import BaseUI
from .magnet import MagnetUI, run_magnet

__all__ = ["BaseUI", "MagnetUI", "run_magnet"]
