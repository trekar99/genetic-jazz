"""
XML Parser for iRealPro MusicXML chord progressions.

This module provides functionality to parse MusicXML files (commonly exported
from iRealPro) and extract chord progressions for use with the genetic
melody generator.
"""

import xml.etree.ElementTree as ET

from src.core import ChordProgression, ChordFactory


# Mapping from MusicXML chord quality to ChordFactory.CHORD_TYPES keys
# Available types: 'maj7', 'min7', 'dom7', 'min7b5', 'dim7', 'minMaj7',
#                  'maj7#5', '7sus4', 'dom7#11'
QUALITY_MAP = {
    # Major 7th -> 'maj7'
    'maj7': 'maj7', 'Maj7': 'maj7', 'M7': 'maj7', 'major-seventh': 'maj7',
    'major': 'maj7', '': 'maj7', 'maj': 'maj7',
    
    # Minor 7th -> 'min7'
    'm7': 'min7', 'min7': 'min7', '-7': 'min7', 'minor-seventh': 'min7',
    'm': 'min7', 'min': 'min7', 'minor': 'min7',
    
    # Dominant 7th -> 'dom7'
    '7': 'dom7', 'dom7': 'dom7', 'dominant': 'dom7', 'dominant-seventh': 'dom7',
    
    # Half-diminished -> 'min7b5'
    'm7b5': 'min7b5', 'min7b5': 'min7b5', '-7b5': 'min7b5', 'mi7b5': 'min7b5',
    'ø': 'min7b5', 'ø7': 'min7b5', 'half-diminished': 'min7b5',
    'half-diminished-seventh': 'min7b5',
    
    # Diminished 7th -> 'dim7'
    'dim7': 'dim7', 'o7': 'dim7', '°7': 'dim7', 'diminished-seventh': 'dim7',
    'dim': 'dim7', 'diminished': 'dim7',
    
    # Minor-Major 7th -> 'minMaj7'
    'mMaj7': 'minMaj7', 'minMaj7': 'minMaj7', '-Maj7': 'minMaj7',
    'minor-major': 'minMaj7', 'minor-major-seventh': 'minMaj7',
    
    # Augmented Major 7th -> 'maj7#5'
    'maj7#5': 'maj7#5', '+maj7': 'maj7#5', 'augmented-seventh': 'maj7#5',
    
    # Dominant sus4 -> '7sus4'
    '7sus4': '7sus4', '7sus': '7sus4', 'sus7': '7sus4', 'sus4': '7sus4',
    'suspended-fourth': '7sus4', 'dominant-suspended-fourth': '7sus4',
    
    # Lydian Dominant -> 'dom7#11'
    '7#11': 'dom7#11', '7(#11)': 'dom7#11', 'dom7#11': 'dom7#11',
    
    # Triads/6th chords -> map to closest 7th chord
    '6': 'maj7', 'maj6': 'maj7', 'major-sixth': 'maj7',
    'm6': 'min7', 'min6': 'min7', 'minor-sixth': 'min7',
    'aug': 'maj7#5', '+': 'maj7#5', 'augmented': 'maj7#5',
}


def _parse_alter(alter_val) -> str:
    """
    Convert MusicXML alter value to accidental string.
    
    Args:
        alter_val: The alter value from MusicXML (can be string, int, or None)
        
    Returns:
        Accidental string: '#', 'b', '##', 'bb', or ''
    """
    if alter_val is None:
        return ""
    val = int(alter_val)
    return {1: "#", -1: "b", 2: "##", -2: "bb"}.get(val, "")


def _map_quality(quality: str) -> str:
    """
    Map MusicXML chord quality to ChordFactory chord type.
    
    Args:
        quality: The chord quality string from MusicXML
        
    Returns:
        ChordFactory chord type identifier
    """
    q = quality.strip() if quality else ""
    
    # Direct lookup
    if q in QUALITY_MAP:
        return QUALITY_MAP[q]
    
    # Fallback pattern matching (order matters for specificity)
    q_lower = q.lower()
    if 'maj7#5' in q_lower or ('+' in q and 'maj7' in q_lower):
        return 'maj7#5'
    if 'mmaj7' in q_lower or 'minmaj7' in q_lower or '-maj7' in q:
        return 'minMaj7'
    if 'maj7' in q_lower or 'm7' in q.upper():
        return 'maj7'
    if 'm7b5' in q_lower or 'ø' in q or 'mi7b5' in q_lower:
        return 'min7b5'
    if 'dim' in q_lower or '°' in q:
        return 'dim7'
    if 'sus' in q_lower:
        return '7sus4'
    if '#11' in q:
        return 'dom7#11'
    if 'm7' in q_lower or 'mi7' in q_lower or 'min7' in q_lower:
        return 'min7'
    if '7' in q:
        return 'dom7'
    if 'm' in q_lower or 'min' in q_lower:
        return 'min7'
    if '+' in q or 'aug' in q_lower:
        return 'maj7#5'
    
    return 'maj7'  # Default fallback


def get_progression_from_xml(xml_path: str) -> ChordProgression:
    """
    Load a chord progression from an iRealPro MusicXML file.
    
    Extracts the first 8 bars with one chord per bar (uses first chord
    if multiple chords exist in a bar).
    
    Args:
        xml_path: Path to the MusicXML file
        
    Returns:
        ChordProgression object with 8 JazzChord objects
        
    Raises:
        FileNotFoundError: If the XML file does not exist
        ET.ParseError: If the XML file is malformed
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Extract song title
    title_node = root.find('.//work-title') or root.find('.//movement-title')
    song_title = title_node.text if title_node is not None else "Unknown"
    
    # Parse first 8 bars, one chord per bar
    part = root.find('part')
    chord_data = []  # List of (root, quality) tuples
    last_chord = None
    
    for measure in list(part.findall('measure'))[:8]:
        harmony = measure.find('harmony')
        if harmony is not None:
            # Extract root note
            root_node = harmony.find('root')
            root_step = root_node.find('root-step').text.upper()  # Ensure uppercase
            alter_node = root_node.find('root-alter')
            alter = _parse_alter(alter_node.text if alter_node is not None else 0)
            chord_root = f"{root_step}{alter}"
            
            # Extract quality
            kind = harmony.find('kind')
            quality = kind.get('text') or kind.text or ""
            
            last_chord = (chord_root, quality)
        
        if last_chord:
            chord_data.append(last_chord)
    
    # Pad to 8 bars if needed
    while len(chord_data) < 8 and last_chord:
        chord_data.append(last_chord)
    
    # Create JazzChord objects using ChordFactory
    chords = [
        ChordFactory.create(root, _map_quality(quality))
        for root, quality in chord_data
    ]
    
    return ChordProgression(chords=chords, name=f"{song_title} (first 8 bars)")


if __name__ == "__main__":
    # Test the parser
    progression = get_progression_from_xml("data/Autumn Leaves.xml")
    print(f"Progression: {progression.name}\n")
    for i, chord in enumerate(progression.chords, 1):
        print(f"Bar {i}: {chord.name}")
