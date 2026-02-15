"""
Pairing strategies for selecting parent pairs during crossover.
"""

from __future__ import annotations

import random
from typing import Callable

from src.core import MelodyGenome

PairingStrategy = Callable[[list[MelodyGenome]], tuple[MelodyGenome, MelodyGenome]]


def random_pairing(parents: list[MelodyGenome]) -> tuple[MelodyGenome, MelodyGenome]:
    """Select two parents uniformly at random."""
    if len(parents) < 2:
        raise ValueError("Pairing requires at least two parents")
    return tuple(random.sample(parents, 2))


def _similarity_score(parent1: MelodyGenome, parent2: MelodyGenome) -> int:
    """Count matching pitch positions between two genomes."""
    return sum(
        1
        for pitch1, pitch2 in zip(parent1.pitches, parent2.pitches)
        if pitch1 == pitch2
    )


def _similarity_pairing(parents: list[MelodyGenome], pick_most_similar: bool) -> tuple[MelodyGenome, MelodyGenome]:
    if len(parents) < 2:
        raise ValueError("Pairing requires at least two parents")

    parent1_index = random.randrange(len(parents))
    parent1 = parents[parent1_index]

    best_index = None
    best_score = None

    for index, candidate in enumerate(parents):
        if index == parent1_index:
            continue

        score = _similarity_score(parent1, candidate)
        if best_score is None:
            best_score = score
            best_index = index

        elif pick_most_similar and score > best_score:
            best_score = score
            best_index = index

        elif (not pick_most_similar) and score < best_score:
            best_score = score
            best_index = index

    if best_index is None:
        return random_pairing(parents)

    return parent1, parents[best_index]


def similarity_pairing(parents: list[MelodyGenome]) -> tuple[MelodyGenome, MelodyGenome]:
    """Pair a parent with its most similar mate."""
    return _similarity_pairing(parents, pick_most_similar=True)


def dissimilarity_pairing(parents: list[MelodyGenome]) -> tuple[MelodyGenome, MelodyGenome]:
    """Pair a parent with its most dissimilar mate."""
    return _similarity_pairing(parents, pick_most_similar=False)


def best_first_last_pairing(parents: list[MelodyGenome]) -> tuple[MelodyGenome, MelodyGenome]:
    """Pair a high-fitness parent with a low-fitness parent.

    Expects the parents list to be sorted by fitness (best to worst).
    """
    if len(parents) < 2:
        raise ValueError("Pairing requires at least two parents")

    top_count = max(1, len(parents) // 4)
    bottom_count = max(1, len(parents) // 4)

    parent1 = random.choice(parents[:top_count])
    parent2 = random.choice(parents[-bottom_count:])

    if parent1 is parent2:
        return random_pairing(parents)

    return parent1, parent2


PAIRING_STRATEGIES: dict[str, PairingStrategy] = {
    "random": random_pairing,
    "similarity": similarity_pairing,
    "dissimilarity": dissimilarity_pairing,
    "best_first_last": best_first_last_pairing,
}


def resolve_pairing_strategy(strategy: str | PairingStrategy) -> PairingStrategy:
    """Resolve a pairing strategy by name or return the provided callable."""
    if callable(strategy):
        return strategy

    if not isinstance(strategy, str):
        raise TypeError("pairing_strategy must be a string or a callable")

    key = strategy.lower()
    if key not in PAIRING_STRATEGIES:
        available = ", ".join(sorted(PAIRING_STRATEGIES.keys()))
        raise ValueError(f"Unknown pairing strategy '{strategy}'. Available: {available}")

    return PAIRING_STRATEGIES[key]
