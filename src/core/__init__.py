"""
Core module containing fundamental data structures and constants.

This module provides:
- Constants for MIDI pitches, rhythmic grid, and structure
- Data classes for chords, progressions, and melody genomes
- Factory for creating jazz chords
"""

from .constants import (
    REST,
    MIN_PITCH,
    MAX_PITCH,
    NOTES_PER_BAR,
    EIGHTH_NOTE_DURATION,
    NUM_BARS,
    TOTAL_NOTES,
)
from .chorddata import JazzChord, ChordProgression, MelodyGenome
from .chordfactory import ChordFactory

__all__ = [
    # Constants
    "REST",
    "MIN_PITCH",
    "MAX_PITCH",
    "NOTES_PER_BAR",
    "EIGHTH_NOTE_DURATION",
    "NUM_BARS",
    "TOTAL_NOTES",
    # Data classes
    "JazzChord",
    "ChordProgression",
    "MelodyGenome",
    # Factory
    "ChordFactory",
]
