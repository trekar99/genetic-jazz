"""
Genetic algorithm for jazz melody generation.

This module provides the GeneticJazzMelodyGenerator class which evolves
melodies using selection, crossover, and mutation operators tailored
for musical applications.
"""

import random

from src.core import (
    REST, MIN_PITCH, MAX_PITCH,
    NUM_BARS, NOTES_PER_BAR, TOTAL_NOTES,
    JazzChord, ChordProgression, MelodyGenome
)
from .fitness import JazzFitnessEvaluator
from .pairing import PairingStrategy, resolve_pairing_strategy


class GeneticJazzMelodyGenerator:
    """
    Generates jazz melodies using a genetic algorithm.
    
    This class evolves a population of melody genomes to find one that best
    fits the given chord progression based on the fitness evaluator.
    
    Genetic Operators:
        - Selection: Fitness-proportionate selection (roulette wheel)
        - Crossover: One-point crossover at bar boundaries
        - Mutation: Random pitch changes with configurable rate
    
    Jazz-Specific Mutations:
        - Random pitch change: Replace with random pitch or rest
        - Chord tone snap: Snap random notes to nearest chord tone
        - Rest toggle: Add or remove rests for rhythmic variation
    
    Attributes:
        progression: The chord progression to generate melodies for
        fitness_evaluator: Evaluator for melody fitness
        population_size: Number of genomes in population
        mutation_rate: Probability of mutation per genome
        elite_size: Number of top genomes preserved each generation
        pairing_strategy: Callable used to select parent pairs
    """
    
    def __init__(
        self,
        progression: ChordProgression,
        fitness_evaluator: JazzFitnessEvaluator,
        population_size: int = 100,
        mutation_rate: float = 0.1,
        elite_size: int = 5,
        pairing_strategy: str | PairingStrategy = "random"
    ):
        """
        Initialize the generator.
        
        Args:
            progression: The chord progression to generate melodies for
            fitness_evaluator: The fitness evaluator to use
            population_size: Size of the population (default: 100)
            mutation_rate: Probability of mutation per genome (default: 0.1)
            elite_size: Number of elite genomes to preserve (default: 5)
            pairing_strategy: Strategy name or callable for pairing parents (default: "random")
        """
        self.progression = progression
        self.fitness_evaluator = fitness_evaluator
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.pairing_strategy = resolve_pairing_strategy(pairing_strategy)
        self._population: list[MelodyGenome] = []
    
    def generate(self, generations: int = 500) -> MelodyGenome:
        """
        Generate a melody using the genetic algorithm.
        
        Args:
            generations: Number of generations to evolve (default: 500)
            
        Returns:
            The best melody genome found after evolution
        """
        self._population = self._initialize_population()
        
        for gen in range(generations):
            # Evaluate and sort by fitness
            fitness_scores = [
                (genome, self.fitness_evaluator.evaluate(genome))
                for genome in self._population
            ]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Elitism: Keep top performers
            new_population = [
                genome.copy() for genome, _ in fitness_scores[:self.elite_size]
            ]

            fitness_by_id = {id(genome): score for genome, score in fitness_scores}
            
            # Select parents and create new population
            parents = self._select_parents()
            parents.sort(
                key=lambda genome: fitness_by_id.get(id(genome), 0.0),
                reverse=True
            )
            
            while len(new_population) < self.population_size:
                parent1, parent2 = self.pairing_strategy(parents)
                child1 = self._crossover(parent1, parent2)
                child2 = self._crossover(parent2, parent1)
                
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            self._population = new_population[:self.population_size]
        
        return self.fitness_evaluator.get_best_genome(self._population)
    
    def _initialize_population(self) -> list[MelodyGenome]:
        """
        Initialize population with semi-random melodies.
        
        Uses smart initialization that biases toward chord tones
        to give the algorithm a head start.
        """
        population = []
        
        for _ in range(self.population_size):
            genome = self._generate_smart_random_genome()
            population.append(genome)
        
        return population
    
    def _generate_smart_random_genome(self) -> MelodyGenome:
        """
        Generate a random genome with bias toward chord tones.
        
        This initialization strategy:
        - 70% chance of chord tone on strong beats
        - 50% chance of any note on weak beats
        - Includes some rests for rhythmic variety
        """
        pitches = []
        
        for bar_idx in range(NUM_BARS):
            chord = self.progression.chords[bar_idx]
            
            for pos in range(NOTES_PER_BAR):
                is_strong_beat = pos in [0, 4]
                
                # Random rest
                if random.random() < 0.3:
                    pitches.append(REST)
                    continue
                
                if is_strong_beat and random.random() < 0.7:
                    # Bias toward chord tone on strong beat
                    pitch = self._random_chord_tone(chord)
                else:
                    # Random pitch
                    pitch = random.randint(MIN_PITCH, MAX_PITCH)
                
                pitches.append(pitch)
        
        return MelodyGenome(pitches=pitches)
    
    def _random_chord_tone(self, chord: JazzChord) -> int:
        """Generate a random pitch that is a chord tone."""
        chord_tone_interval = random.choice(chord.chord_tones)
        octave = random.choice([60, 72])  # C4 or C5 octave
        return octave + chord.root + chord_tone_interval
    
    def _select_parents(self) -> list[MelodyGenome]:
        """Select parents for breeding using fitness-proportionate selection."""
        fitness_values = [
            max(0.01, self.fitness_evaluator.evaluate(genome))
            for genome in self._population
        ]
        
        return random.choices(
            self._population,
            weights=fitness_values,
            k=self.population_size
        )
    
    def _crossover(self, parent1: MelodyGenome, parent2: MelodyGenome) -> MelodyGenome:
        """
        Perform one-point crossover at a bar boundary.
        
        Crossing over at bar boundaries ensures that phrases remain intact,
        which tends to preserve musical coherence.
        """
        cut_bar = random.randint(1, NUM_BARS - 1)
        cut_index = cut_bar * NOTES_PER_BAR
        
        new_pitches = parent1.pitches[:cut_index] + parent2.pitches[cut_index:]
        return MelodyGenome(pitches=new_pitches)
    
    def _mutate(self, genome: MelodyGenome) -> MelodyGenome:
        """
        Apply mutation operators to a genome.
        
        Mutation types (selected randomly):
        - Random pitch change (50%): Replace with random pitch or rest
        - Chord tone snap (30%): Snap to nearest chord tone
        - Rest toggle (20%): Toggle between note and rest
        """
        if random.random() >= self.mutation_rate:
            return genome
        
        mutated = genome.copy()
        mutation_type = random.random()
        
        if mutation_type < 0.5:
            # Random pitch change
            idx = random.randint(0, TOTAL_NOTES - 1)
            if random.random() < 0.2:
                mutated.pitches[idx] = REST
            else:
                mutated.pitches[idx] = random.randint(MIN_PITCH, MAX_PITCH)
        
        elif mutation_type < 0.8:
            # Chord tone snap
            idx = random.randint(0, TOTAL_NOTES - 1)
            bar_idx = idx // NOTES_PER_BAR
            chord = self.progression.chords[bar_idx]
            mutated.pitches[idx] = self._random_chord_tone(chord)
        
        else:
            # Rest toggle
            idx = random.randint(0, TOTAL_NOTES - 1)
            if mutated.pitches[idx] == REST:
                bar_idx = idx // NOTES_PER_BAR
                chord = self.progression.chords[bar_idx]
                mutated.pitches[idx] = self._random_chord_tone(chord)
            else:
                mutated.pitches[idx] = REST
        
        return mutated
