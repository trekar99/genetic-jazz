"""
Constants for the Genetic Jazz Melody Generator.

This module defines all the musical and structural constants used throughout
the application, including MIDI pitch ranges, rhythmic grid settings, and
the number of bars in a progression.
"""

# MIDI pitch constants
REST = -1       # Represents a rest in the melody
MIN_PITCH = 60  # C4
MAX_PITCH = 84  # C6

# Rhythmic grid constants
NOTES_PER_BAR = 8           # Eighth notes in a 4/4 bar
EIGHTH_NOTE_DURATION = 0.5  # In quarter note units

# Structure constants
NUM_BARS = 8                          # Number of bars in the progression
TOTAL_NOTES = NOTES_PER_BAR * NUM_BARS  # Total notes in a melody
