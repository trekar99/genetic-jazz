"""
Utility functions for score creation and export.

This module provides helper functions for creating music21 scores from
melody genomes and chord progressions, and for exporting to various
formats (MIDI, PNG).
"""
import re
import music21

from src.core import (
    REST, NUM_BARS, NOTES_PER_BAR, EIGHTH_NOTE_DURATION,
    ChordProgression, MelodyGenome
)


def create_jazz_score(
    melody_genome: MelodyGenome,
    progression: ChordProgression
) -> music21.stream.Score:
    """
    Create a music21 score from a melody genome and chord progression.
    
    Creates a two-part score with:
    - Melody part: The evolved melody with proper note durations
    - Chord part: Block chords with chord symbols
    
    Args:
        melody_genome: The evolved melody
        progression: The chord progression
        
    Returns:
        A music21 Score object with melody and chord parts
    """
    score = music21.stream.Score()
    score.metadata = music21.metadata.Metadata()
    score.metadata.title = f"Jazz Melody over {progression.name}"
    score.metadata.composer = "Genetic Algorithm"
    
    # Create melody part
    melody_part = music21.stream.Part()
    melody_part.partName = "Melody"
    melody_part.append(music21.meter.TimeSignature('4/4'))
    
    # Convert genome to notes, consolidating consecutive identical pitches
    current_duration = 0.0
    i = 0
    while i < len(melody_genome.pitches):
        pitch = melody_genome.pitches[i]
        
        # Consolidate consecutive identical pitches or rests
        duration = EIGHTH_NOTE_DURATION
        j = i + 1
        while j < len(melody_genome.pitches) and \
              melody_genome.pitches[j] == pitch and \
              j % NOTES_PER_BAR != 0:  # Don't cross bar lines
            duration += EIGHTH_NOTE_DURATION
            j += 1
        
        if pitch == REST:
            rest = music21.note.Rest(quarterLength=duration)
            rest.offset = current_duration
            melody_part.append(rest)
        else:
            note = music21.note.Note(pitch, quarterLength=duration)
            note.offset = current_duration
            melody_part.append(note)
        
        current_duration += duration
        i = j
    
    # Create chord part
    chord_part = music21.stream.Part()
    chord_part.partName = "Chords"
    chord_part.append(music21.meter.TimeSignature('4/4'))
    
    current_offset = 0.0
    for chord_obj in progression.chords:
        # Build chord notes in bass register
        chord_notes = []
        for interval in chord_obj.chord_tones:
            midi_pitch = 48 + chord_obj.root + interval
            chord_notes.append(midi_pitch)
        
        m21_chord = music21.chord.Chord(chord_notes, quarterLength=4)
        m21_chord.offset = current_offset
        
        # Add chord symbol - convert 'b' to '-' for music21 compatibility
        # music21 uses '-' for flats (e.g., 'B-maj7' not 'Bbmaj7')
        chord_name_m21 = re.sub(r'([A-G])b', r'\1-', chord_obj.name)
        chord_symbol = music21.harmony.ChordSymbol(chord_name_m21)
        chord_symbol.offset = current_offset
        chord_part.append(chord_symbol)
        chord_part.append(m21_chord)
        
        current_offset += 4
    
    score.append(melody_part)
    score.append(chord_part)
    
    return score


def export_to_midi(score: music21.stream.Score, filename: str) -> str:
    """
    Export a music21 score to MIDI file.
    
    Args:
        score: The score to export
        filename: Output filename (with or without .mid extension)
        
    Returns:
        The full path to the exported file
    """
    if not filename.endswith('.mid') and not filename.endswith('.midi'):
        filename += '.mid'
    
    midi_file = music21.midi.translate.music21ObjectToMidiFile(score)
    midi_file.open(filename, 'wb')
    midi_file.write()
    midi_file.close()
    
    return filename


def export_to_png(score: music21.stream.Score, filename: str) -> str:
    """
    Export a music21 score to PNG image.
    
    Note: This requires MuseScore or LilyPond to be installed on the system.
    
    Args:
        score: The score to export
        filename: Output filename (without extension)
        
    Returns:
        The full path to the exported PNG file
        
    Raises:
        Exception: If no music notation software is available
    """
    if filename.endswith('.png'):
        filename = filename[:-4]
    
    # Use music21's write method to export as PNG
    output_path = score.write('musicxml.png', fp=filename)
    
    return str(output_path)
