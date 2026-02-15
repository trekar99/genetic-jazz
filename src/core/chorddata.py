"""
Data classes for representing jazz chords, progressions, and melodies.

This module provides the core data structures used throughout the application:
- JazzChord: Represents a single jazz chord with its musical properties
- ChordProgression: Represents an 8-bar chord progression
- MelodyGenome: Represents a melody as a genetic sequence
"""

from dataclasses import dataclass, field

from .constants import NUM_BARS, NOTES_PER_BAR, TOTAL_NOTES, REST


@dataclass(frozen=True)
class JazzChord:
    """
    Represents a jazz 7th chord with its musical properties.
    
    Attributes:
        name: Display name of the chord (e.g., "Dm7", "G7", "Cmaj7")
        root: Root note as pitch class (0-11, where C=0)
        chord_tones: Tuple of intervals from root that are chord tones (1, 3, 5, 7)
        tensions: Tuple of available tension intervals (9, 11, 13)
        avoid_notes: Tuple of intervals that clash with the chord
        
    Note:
        All intervals are in semitones from the root.
    """
    name: str
    root: int  # Pitch class 0-11 (C=0, C#=1, ..., B=11)
    chord_tones: tuple[int, ...]  # Intervals: root, 3rd, 5th, 7th
    tensions: tuple[int, ...]  # Available tensions: 9, 11, 13
    avoid_notes: tuple[int, ...]  # Notes to avoid


@dataclass
class ChordProgression:
    """
    Represents an 8-bar jazz chord progression.
    
    Attributes:
        chords: List of 8 JazzChord objects, one per bar
        name: Optional name for the progression
        
    Raises:
        ValueError: If the progression does not have exactly NUM_BARS chords
    """
    chords: list[JazzChord]
    name: str = "Unnamed Progression"
    
    def __post_init__(self):
        if len(self.chords) != NUM_BARS:
            raise ValueError(f"Progression must have exactly {NUM_BARS} chords")


@dataclass
class MelodyGenome:
    """
    Represents a melody as a genetic sequence.
    
    The melody is encoded as a fixed-grid sequence of MIDI pitches.
    Each bar contains NOTES_PER_BAR slots, each slot is an eighth note.
    A value of REST (-1) indicates a rest.
    
    Attributes:
        pitches: List of MIDI pitch values (or REST) for each eighth note slot
    """
    pitches: list[int] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.pitches:
            self.pitches = [REST] * TOTAL_NOTES
    
    def get_bar(self, bar_index: int) -> list[int]:
        """
        Get pitches for a specific bar.
        
        Args:
            bar_index: Zero-indexed bar number (0-7)
            
        Returns:
            List of MIDI pitches for the specified bar
        """
        start = bar_index * NOTES_PER_BAR
        return self.pitches[start:start + NOTES_PER_BAR]
    
    def copy(self) -> 'MelodyGenome':
        """Create a deep copy of this genome."""
        return MelodyGenome(pitches=self.pitches.copy())
