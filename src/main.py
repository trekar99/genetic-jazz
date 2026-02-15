"""
Main entry point for the Genetic Jazz Melody Generator.

This module demonstrates the Genetic Jazz Melody Generator by:
1. Creating a chord progression (from XML file or preset)
2. Setting up the fitness evaluator with weighted metrics
3. Running the genetic algorithm to evolve a melody
4. Creating a music21 score with melody and chords
5. Exporting the result to a MIDI file
6. Optionally displaying the score
"""

import sys
from pathlib import Path

# Add parent directory to path for imports when running from src/
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import REST, NUM_BARS
from src.genetic import JazzFitnessEvaluator, GeneticJazzMelodyGenerator
from src.progressions import get_progression_from_xml, get_ii_v_i_progression
from src.utils import create_jazz_score, export_to_midi


def main():
    """Main function of the Genetic Jazz Melody Generator."""
    
    print("Genetic Jazz Melody Generator")
    print("=" * 40)
    
    # Load chord progression from XML file
    progression = get_progression_from_xml("data/A Felicidade 1.xml")
    
    print(f"\nChord Progression: {progression.name}")
    print("Bars: ", end="")
    for i, chord in enumerate(progression.chords, 1):
        print(f"| {chord.name} ", end="")
    print("|")
    
    # Configure fitness evaluator
    # Weights determine the importance of each fitness metric
    weights = {
        'chord_tone_emphasis': 0.15,  # Emphasize chord tones on strong beats
        'tension_usage': 0.15,        # Controlled use of 9ths, 11ths, 13ths
        'avoid_wrong_notes': 0.15,    # Penalize clashing notes
        'call_and_response': 0.15,    # Motif repetition and variation
        'melodic_motion': 0.10,       # Prefer stepwise motion
        'arpeggio_scale_mix': 0.05,   # Balanced arpeggios and scales
        'phrase_contour': 0.10,       # Coherent melodic shapes
        'note_density': 0.10,         # Balanced note/rest ratio
        'range_fitness': 0.05         # Stay in playable range
    }
    
    fitness_evaluator = JazzFitnessEvaluator(
        progression=progression,
        weights=weights
    )
    
    print(f"\nFitness Weights:")
    for func, weight in weights.items():
        print(f"  {func}: {weight:.2f}")
    
    # Configure genetic algorithm
    pairing_strategy = "random"
    generator = GeneticJazzMelodyGenerator(
        progression=progression,
        fitness_evaluator=fitness_evaluator,
        population_size=100,
        mutation_rate=0.15,
        elite_size=5,
        pairing_strategy=pairing_strategy
    )
    
    print(f"\nGenetic Algorithm Parameters:")
    print(f"  Population size: {generator.population_size}")
    print(f"  Mutation rate: {generator.mutation_rate}")
    print(f"  Elite size: {generator.elite_size}")
    print(f"  Pairing strategy: {pairing_strategy}")
    
    # Run evolution
    print("\nEvolving melody...")
    generations = 1000
    best_melody = generator.generate(generations=generations)
    
    final_fitness = fitness_evaluator.evaluate(best_melody)
    print(f"Evolution complete after {generations} generations")
    print(f"Best melody fitness score: {final_fitness:.4f}")
    
    # Create and export score
    score = create_jazz_score(best_melody, progression)
    
    midi_filename = "generated_jazz_melody.mid"
    exported_path = export_to_midi(score, midi_filename)
    print(f"\nMIDI file exported: {exported_path}")
    
    # Print the generated melody
    print("\nGenerated Melody (MIDI pitches per bar):")
    for bar_idx in range(NUM_BARS):
        bar = best_melody.get_bar(bar_idx)
        chord = progression.chords[bar_idx]
        bar_display = [
            f"{p}" if p != REST else "R" 
            for p in bar
        ]
        print(f"  Bar {bar_idx + 1} ({chord.name:6}): {bar_display}")
    
    # Display score (optional - requires music21 viewer setup)
    print("\nAttempting to display the generated score...")
    try:
        score.show()
    except Exception as e:
        print(f"Could not display score (viewer may not be configured): {e}")
        print("The MIDI file can be opened in MuseScore or any MIDI player.")
    
    print("\nGeneration complete.")


if __name__ == "__main__":
    main()
