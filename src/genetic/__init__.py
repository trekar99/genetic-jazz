"""
Genetic algorithm module for melody generation.

This module provides:
- JazzFitnessEvaluator: Evaluates melody fitness against chord progressions
- GeneticJazzMelodyGenerator: Evolves melodies using genetic algorithms
"""

from .fitness import JazzFitnessEvaluator, FITNESS_WEIGHTS_CONFIG, get_default_weights
from .generator import GeneticJazzMelodyGenerator
from .pairing import PAIRING_STRATEGIES, PairingStrategy, resolve_pairing_strategy

__all__ = [
    "JazzFitnessEvaluator",
    "GeneticJazzMelodyGenerator",
    "FITNESS_WEIGHTS_CONFIG",
    "get_default_weights",
    "PAIRING_STRATEGIES",
    "PairingStrategy",
    "resolve_pairing_strategy",
]
