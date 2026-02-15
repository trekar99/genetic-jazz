"""
Chord progression sources module.

This module provides functions to load chord progressions from:
- Preset progressions (common jazz standards)
- iRealPro MusicXML files
"""

from .presets import (
    get_ii_v_i_progression,
    get_ii_v_i_vi7_ii_v_iii_progression,
    get_autumn_leaves_progression,
    get_minor_blues_progression,
)
from .xmlparser import get_progression_from_xml

__all__ = [
    "get_ii_v_i_progression",
    "get_ii_v_i_vi7_ii_v_iii_progression",
    "get_autumn_leaves_progression",
    "get_minor_blues_progression",
    "get_progression_from_xml",
]
