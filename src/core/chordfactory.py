"""
Factory for creating jazz chord objects.

This module provides a factory class for creating JazzChord objects from
root note names and chord type identifiers, supporting common jazz chord
types including major 7th, minor 7th, dominant 7th, and alterations.
"""

from .chorddata import JazzChord


class ChordFactory:
    """
    Factory for creating jazz 7th chords.
    
    Supported chord types:
        - maj7: Major 7th (1, 3, 5, 7)
        - min7: Minor 7th (1, b3, 5, b7)
        - dom7: Dominant 7th (1, 3, 5, b7)
        - min7b5: Half-diminished (1, b3, b5, b7)
        - dim7: Diminished 7th (1, b3, b5, bb7)
        - minMaj7: Minor-Major 7th (1, b3, 5, 7)
        - maj7#5: Lydian Augmented (1, 3, #5, 7)
        - 7sus4: Dominant Suspended (1, 4, 5, b7)
        - dom7#11: Lydian Dominant (1, 3, 5, b7, #11)
    
    Example:
        >>> chord = ChordFactory.create("D", "min7")  # Creates Dm7
        >>> print(chord.name)
        Dm7
    """
    
    # Pitch class mapping from note names to semitones (C=0)
    NOTE_TO_PC = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'Fb': 4, 'E#': 5, 'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10,
        'B': 11, 'Cb': 11
    }
    
    # Chord type definitions: (chord_tones, tensions, avoid_notes)
    # All intervals in semitones from root
    CHORD_TYPES = {
        'maj7': (               # Ionian/Lydian
            (0, 4, 7, 11),      # 1, 3, 5, 7
            (2, 6, 9),          # 9, #11, 13
            (5,)                # 11 (avoid - clashes with 3rd)
        ),
        'min7': (               # Dorian/Phrygian
            (0, 3, 7, 10),      # 1, b3, 5, b7
            (2, 5, 9),          # 9, 11, 13
            (6,)                # b13 (can clash in some contexts)
        ),
        'dom7': (               # Mixolydian
            (0, 4, 7, 10),      # 1, 3, 5, b7
            (2, 9),             # 9, 13
            (5,)                # 11 (avoid - clashes with 3rd)
        ),
        'min7b5': (             # Half-diminished (Locrian)
            (0, 3, 6, 10),      # 1, b3, b5, b7
            (2, 5, 8),          # 9, 11, b13
            ()                  # No strict avoid notes
        ),
        'dim7': (               # Diminished (Whole-Half Diminished)
            (0, 3, 6, 9),       # 1, b3, b5, bb7
            (2, 5, 8),          # 9, 11, b13
            ()                  # Symmetric chord
        ),
        'minMaj7': (            # Melodic Minor
            (0, 3, 7, 11),      # 1, b3, 5, 7
            (2, 5, 9),          # 9, 11, 13
            (6,)                # b13 (can clash in some contexts)
        ),
        'maj7#5': (             # Lydian Augmented
            (0, 4, 8, 11),      # 1, 3, #5, 7
            (2, 6),             # 9, #11
            (5,)                # 11 (avoid - clashes with 3rd)
        ),
        '7sus4': (              # Dominant Sus4
            (0, 5, 7, 10),      # 1, 4, 5, b7
            (2, 9),             # 9, 13
            (4,)                # 3 (avoid - clashes with sus4)
        ),
        'dom7#11': (            # Lydian Dominant
            (0, 4, 7, 10),      # 1, 3, 5, b7
            (2, 6, 9),          # 9, #11, 13
            (5,)                # 11 (avoid - clashes with 3rd)
        ),
    }
    
    # Display name suffixes for each chord type
    _TYPE_DISPLAY = {
        'maj7': 'maj7',
        'min7': 'm7',
        'dom7': '7',
        'min7b5': 'm7b5',
        'dim7': 'dim7',
        'minMaj7': 'mMaj7',
        'maj7#5': 'maj7#5',
        '7sus4': '7sus4',
        'dom7#11': '7#11',
    }
    
    @classmethod
    def create(cls, root_name: str, chord_type: str) -> JazzChord:
        """
        Create a JazzChord from root name and type.
        
        Args:
            root_name: Root note name (e.g., "C", "F#", "Bb")
            chord_type: Chord type identifier (e.g., "maj7", "min7", "dom7")
            
        Returns:
            JazzChord object with the specified root and type
            
        Raises:
            ValueError: If root_name or chord_type is not recognized
        """
        if root_name not in cls.NOTE_TO_PC:
            raise ValueError(f"Unknown root note: {root_name}")
        if chord_type not in cls.CHORD_TYPES:
            raise ValueError(f"Unknown chord type: {chord_type}")
        
        root_pc = cls.NOTE_TO_PC[root_name]
        chord_tones, tensions, avoid_notes = cls.CHORD_TYPES[chord_type]
        
        # Create display name
        name = f"{root_name}{cls._TYPE_DISPLAY.get(chord_type, chord_type)}"
        
        return JazzChord(
            name=name,
            root=root_pc,
            chord_tones=chord_tones,
            tensions=tensions,
            avoid_notes=avoid_notes
        )
