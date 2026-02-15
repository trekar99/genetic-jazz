"""
Preset chord progressions for testing and demonstration.

This module provides common jazz chord progressions that can be used
without loading from XML files. These are useful for testing the
genetic algorithm and for demonstration purposes.
"""

from src.core import ChordProgression, ChordFactory


def get_ii_v_i_progression() -> ChordProgression:
    """
    Create a classic ii-V-I-I progression in C, repeated twice.
    
    This is one of the most common jazz progressions:
    | Dm7 | G7 | Cmaj7 | Cmaj7 | Dm7 | G7 | Cmaj7 | Cmaj7 |
    
    Returns:
        ChordProgression with 8 bars of ii-V-I in C major
    """
    chords = [
        ChordFactory.create("D", "min7"),   # Bar 1: ii
        ChordFactory.create("G", "dom7"),   # Bar 2: V
        ChordFactory.create("C", "maj7"),   # Bar 3: I
        ChordFactory.create("C", "maj7"),   # Bar 4: I
        ChordFactory.create("D", "min7"),   # Bar 5: ii
        ChordFactory.create("G", "dom7"),   # Bar 6: V
        ChordFactory.create("C", "maj7"),   # Bar 7: I
        ChordFactory.create("C", "maj7"),   # Bar 8: I
    ]
    return ChordProgression(chords=chords, name="ii-V-I in C")


def get_ii_v_i_vi7_ii_v_iii_progression() -> ChordProgression:
    """
    Create a ii-V-I-vi7 progression variation in C.
    
    A common jazz turnaround variation:
    | Dm7 | G7 | Cmaj7 | Am7 | Dm7 | G7 | Em7 | Em7 |
    
    Returns:
        ChordProgression with 8 bars of ii-V-I-vi turnaround
    """
    chords = [
        ChordFactory.create("D", "min7"),   # Bar 1: ii
        ChordFactory.create("G", "dom7"),   # Bar 2: V
        ChordFactory.create("C", "maj7"),   # Bar 3: I
        ChordFactory.create("A", "min7"),   # Bar 4: vi
        ChordFactory.create("D", "min7"),   # Bar 5: ii
        ChordFactory.create("G", "dom7"),   # Bar 6: V
        ChordFactory.create("E", "min7"),   # Bar 7: iii
        ChordFactory.create("E", "min7"),   # Bar 8: iii
    ]
    return ChordProgression(chords=chords, name="ii-V-I-vi7 Turnaround in C")


def get_autumn_leaves_progression() -> ChordProgression:
    """
    First 8 bars of "Autumn Leaves" changes (in G minor/Bb major).
    
    | Cm7 | F7 | Bbmaj7 | Ebmaj7 | Am7b5 | D7 | Gm7 | Gm7 |
    
    Returns:
        ChordProgression with first 8 bars of Autumn Leaves
    """
    chords = [
        ChordFactory.create("C", "min7"),    # Bar 1
        ChordFactory.create("F", "dom7"),    # Bar 2
        ChordFactory.create("Bb", "maj7"),   # Bar 3
        ChordFactory.create("Eb", "maj7"),   # Bar 4
        ChordFactory.create("A", "min7b5"),  # Bar 5
        ChordFactory.create("D", "dom7"),    # Bar 6
        ChordFactory.create("G", "min7"),    # Bar 7
        ChordFactory.create("G", "min7"),    # Bar 8
    ]
    return ChordProgression(chords=chords, name="Autumn Leaves (first 8 bars)")


def get_minor_blues_progression() -> ChordProgression:
    """
    A minor blues variant in C minor.
    
    | Cm7 | Cm7 | Cm7 | Cm7 | Fm7 | Fm7 | Cm7 | Cm7 |
    
    First 8 bars of a 12-bar minor blues.
    
    Returns:
        ChordProgression with first 8 bars of minor blues in C
    """
    chords = [
        ChordFactory.create("C", "min7"),   # Bar 1
        ChordFactory.create("C", "min7"),   # Bar 2
        ChordFactory.create("C", "min7"),   # Bar 3
        ChordFactory.create("C", "min7"),   # Bar 4
        ChordFactory.create("F", "min7"),   # Bar 5
        ChordFactory.create("F", "min7"),   # Bar 6
        ChordFactory.create("C", "min7"),   # Bar 7
        ChordFactory.create("C", "min7"),   # Bar 8
    ]
    return ChordProgression(chords=chords, name="Minor Blues in C (first 8 bars)")
