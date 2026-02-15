"""
Fitness evaluation for jazz melodies.

This module provides the JazzFitnessEvaluator class which evaluates the
musical quality of generated melodies against chord progressions using
multiple weighted fitness functions.
"""

from typing import Optional

from src.core import (
    NUM_BARS, NOTES_PER_BAR, REST,
    JazzChord, ChordProgression, MelodyGenome
)


# =============================================================================
# FITNESS WEIGHTS CONFIGURATION
# =============================================================================
# To add a new fitness function:
#   1. Add an entry to FITNESS_WEIGHTS_CONFIG below
#   2. Implement the _function_key() method in JazzFitnessEvaluator
# That's it! The webapp and frontend will automatically pick it up.
# =============================================================================

FITNESS_WEIGHTS_CONFIG = [
    {
        'key': 'chord_tone_emphasis',
        'label': 'Chord Tone Emphasis',
        'default': 0.15,
        'description': 'Reward notes that are chord tones'
    },
    {
        'key': 'tension_usage',
        'label': 'Tension Usage',
        'default': 0.15,
        'description': 'Reward appropriate use of tension notes'
    },
    {
        'key': 'avoid_wrong_notes',
        'label': 'Avoid Wrong Notes',
        'default': 0.15,
        'description': 'Penalize notes that clash with the chord'
    },
    {
        'key': 'call_and_response',
        'label': 'Call and Response',
        'default': 0.15,
        'description': 'Reward melodic phrases that exhibit call and response patterns'
    },
    {
        'key': 'melodic_motion',
        'label': 'Melodic Motion',
        'default': 0.10,
        'description': 'Reward smooth melodic lines with occasional leaps'
    },
    {
        'key': 'arpeggio_scale_mix',
        'label': 'Arpeggio-Scale Mix',
        'default': 0.05,
        'description': 'Reward a good mix of arpeggiated and scalar motion'
    },
    {
        'key': 'phrase_contour',
        'label': 'Phrase Contour',
        'default': 0.10,
        'description': 'Reward coherent phrase shapes'
    },
    {
        'key': 'note_density',
        'label': 'Note Density',
        'default': 0.10,
        'description': 'Reward appropriate balance of notes and rests'
    },
    {
        'key': 'range_fitness',
        'label': 'Range Fitness',
        'default': 0.05,
        'description': 'Keep melody within a comfortable playing range'
    },
]


def get_default_weights() -> dict[str, float]:
    """Get default weights dictionary from config."""
    return {item['key']: item['default'] for item in FITNESS_WEIGHTS_CONFIG}


class JazzFitnessEvaluator:
    """
    Evaluates the fitness of a melody genome against a jazz chord progression.
    
    This evaluator uses multiple fitness functions, each capturing a different
    aspect of what makes a good jazz melody. The functions are weighted and
    combined into a single fitness score.
    
    Design Philosophy:
        The fitness functions are designed to capture musical intuitions about
        jazz melody writing:
        
        1. Harmonic compatibility - The melody should fit the chords
        2. Rhythmic emphasis - Important notes on important beats
        3. Call and response - Interactive melodic phrases
        4. Melodic motion - Smooth lines with occasional leaps
        5. Phrase structure - Coherent musical phrases
        6. Range and playability - Practical considerations
    
    Attributes:
        progression: The chord progression to evaluate against
        weights: Dictionary mapping fitness function names to their weights
    """
    
    def __init__(
        self,
        progression: ChordProgression,
        weights: Optional[dict[str, float]] = None
    ):
        """
        Initialize the fitness evaluator.
        
        Args:
            progression: The chord progression to evaluate melodies against
            weights: Optional custom weights for fitness functions. If not
                provided, default weights optimized for jazz are used.
        """
        self.progression = progression
        
        # Default weights from centralized config
        self.weights = weights or get_default_weights()
    
    def evaluate(self, genome: MelodyGenome) -> float:
        """
        Calculate the overall fitness score for a melody genome.
        
        Args:
            genome: The melody genome to evaluate
            
        Returns:
            Float between 0 and 1 representing fitness (higher is better)
        """
        total = sum(
            self.weights[func] * getattr(self, f"_{func}")(genome)
            for func in self.weights
        )
        return total
    
    def get_best_genome(self, genomes: list[MelodyGenome]) -> MelodyGenome:
        """Return the genome with the highest fitness score."""
        return max(genomes, key=self.evaluate)
    
    def _get_pitch_class(self, midi_pitch: int) -> int:
        """Convert MIDI pitch to pitch class (0-11)."""
        return midi_pitch % 12
    
    def _is_chord_tone(self, pitch: int, chord: JazzChord) -> bool:
        """Check if a pitch is a chord tone of the given chord."""
        if pitch == REST:
            return False
        pc = self._get_pitch_class(pitch)
        relative_pc = (pc - chord.root) % 12
        return relative_pc in chord.chord_tones
    
    def _is_tension(self, pitch: int, chord: JazzChord) -> bool:
        """Check if a pitch is an available tension of the given chord."""
        if pitch == REST:
            return False
        pc = self._get_pitch_class(pitch)
        relative_pc = (pc - chord.root) % 12
        return relative_pc in chord.tensions
    
    def _is_avoid_note(self, pitch: int, chord: JazzChord) -> bool:
        """Check if a pitch should be avoided against the given chord."""
        if pitch == REST:
            return False
        pc = self._get_pitch_class(pitch)
        relative_pc = (pc - chord.root) % 12
        return relative_pc in chord.avoid_notes
    
    def _chord_tone_emphasis(self, genome: MelodyGenome) -> float:
        """
        Evaluate emphasis of chord tones on strong beats.
        
        Checks if notes on beats 1 and 3 (the strong beats in 4/4) are
        chord tones of the current harmony. In jazz, strong beats typically
        feature chord tones to clearly outline the harmony.
        
        Returns:
            Score between 0 and 1
        """
        score = 0
        checks = 0
        
        for bar_idx in range(NUM_BARS):
            chord = self.progression.chords[bar_idx]
            bar = genome.get_bar(bar_idx)
            
            # Strong beats: positions 0 (beat 1) and 4 (beat 3) in eighth-note grid
            strong_beat_positions = [0, 4]
            
            for pos in strong_beat_positions:
                pitch = bar[pos]
                if pitch != REST:
                    checks += 1
                    if self._is_chord_tone(pitch, chord):
                        score += 1
                    elif self._is_tension(pitch, chord):
                        score += 0.5  # Tensions on strong beats are acceptable
        
        return score / checks if checks > 0 else 0.5
    
    def _tension_usage(self, genome: MelodyGenome) -> float:
        """
        Evaluate the controlled use of tensions (9ths, 11ths, 13ths).
        
        Measures whether tensions are used appropriately - present but not
        overwhelming. The ideal ratio is roughly 20-40% tensions, which adds
        color and sophistication without sounding ungrounded.
        
        Returns:
            Score between 0 and 1
        """
        tension_count = 0
        total_notes = 0
        
        for bar_idx in range(NUM_BARS):
            chord = self.progression.chords[bar_idx]
            bar = genome.get_bar(bar_idx)
            
            for pitch in bar:
                if pitch != REST:
                    total_notes += 1
                    if self._is_tension(pitch, chord):
                        tension_count += 1
        
        if total_notes == 0:
            return 0
        
        tension_ratio = tension_count / total_notes
        
        # Score peaks at 30% and decreases on either side
        optimal = 0.30
        if tension_ratio <= optimal:
            return tension_ratio / optimal
        else:
            excess = tension_ratio - optimal
            return max(0, 1 - (excess / 0.4))
    
    def _avoid_wrong_notes(self, genome: MelodyGenome) -> float:
        """
        Penalize notes that clash with the chord.
        
        Checks for notes that are neither chord tones nor tensions,
        especially the designated "avoid notes" for each chord type.
        Avoid notes receive a heavier penalty as they create harsh dissonance.
        
        Returns:
            Score between 0 and 1 (higher means fewer wrong notes)
        """
        wrong_note_penalty = 0
        total_notes = 0
        
        for bar_idx in range(NUM_BARS):
            chord = self.progression.chords[bar_idx]
            bar = genome.get_bar(bar_idx)
            
            for pitch in bar:
                if pitch != REST:
                    total_notes += 1
                    
                    if self._is_avoid_note(pitch, chord):
                        wrong_note_penalty += 1.0  # Heavy penalty
                    elif not self._is_chord_tone(pitch, chord) and \
                         not self._is_tension(pitch, chord):
                        # Chromatic passing tone - mild penalty
                        wrong_note_penalty += 0.3
        
        if total_notes == 0:
            return 0.5
        
        max_penalty = total_notes
        return 1 - (wrong_note_penalty / max_penalty)
    
    def _call_and_response(self, genome: MelodyGenome) -> float:
        """
        Evaluate call-and-response phrasing structure with appropriate space.
        
        Checks for the classic jazz phrasing structure:
        - Bars 1-2: Active "call" phrase
        - Bars 3-4: Space/rest or simple sustain
        - Bars 5-6: "Response" phrase (variation)
        - Bars 7-8: Resolution
        
        The call-and-response structure tries to creates musical conversation
        It's used to allows the rhythm section to interact and giving the melody shape and direction.
        
        Returns:
            Score between 0 and 1
        """
        # Calculate density for each 2-bar phrase
        phrase_densities = []
        for phrase_idx in range(4):
            start_bar = phrase_idx * 2
            note_count = 0
            for bar_idx in range(start_bar, start_bar + 2):
                bar = genome.get_bar(bar_idx)
                note_count += sum(1 for p in bar if p != REST)
            density = note_count / (2 * NOTES_PER_BAR)
            phrase_densities.append(density)
        
        score = 0
        
        # Phrase 1 (bars 1-2): Should be active - "call"
        # Optimal density: 40-70%
        if 0.4 <= phrase_densities[0] <= 0.7:
            score += 0.25
        elif 0.3 <= phrase_densities[0] <= 0.8:
            score += 0.15
        
        # Phrase 2 (bars 3-4): Should have space - "breath"
        # Optimal density: 20-50%
        if 0.2 <= phrase_densities[1] <= 0.5:
            score += 0.25
        elif phrase_densities[1] < phrase_densities[0]:
            score += 0.15  # At least less dense than call
        
        # Phrase 3 (bars 5-6): Should be active again - "response"
        # Optimal density: 40-70%
        if 0.4 <= phrase_densities[2] <= 0.7:
            score += 0.25
        elif 0.3 <= phrase_densities[2] <= 0.8:
            score += 0.15
        
        # Phrase 4 (bars 7-8): Resolution - can vary
        # Should have some activity but end with space
        bar7 = genome.get_bar(6)
        bar8 = genome.get_bar(7)
        bar7_density = sum(1 for p in bar7 if p != REST) / NOTES_PER_BAR
        bar8_density = sum(1 for p in bar8 if p != REST) / NOTES_PER_BAR
        
        if bar7_density > bar8_density:  # Winding down
            score += 0.25
        elif 0.2 <= phrase_densities[3] <= 0.6:
            score += 0.15
        
        return score
    
    def _melodic_motion(self, genome: MelodyGenome) -> float:
        """
        Evaluate stepwise motion vs. excessive leaps.
        
        Measures the intervals between consecutive notes, rewarding stepwise
        motion (seconds) and small leaps (thirds), while penalizing large
        leaps (greater than a fifth). Jazz melodies typically flow smoothly
        with occasional leaps for emphasis.
        
        Returns:
            Score between 0 and 1
        """
        score = 0
        intervals = 0
        
        prev_pitch = None
        for pitch in genome.pitches:
            if pitch != REST:
                if prev_pitch is not None:
                    interval = abs(pitch - prev_pitch)
                    intervals += 1
                    
                    if interval <= 2:  # Step (minor/major 2nd)
                        score += 1.0
                    elif interval <= 4:  # Third
                        score += 0.9
                    elif interval <= 5:  # Fourth
                        score += 0.7
                    elif interval <= 7:  # Fifth
                        score += 0.5
                    elif interval <= 9:  # Sixth
                        score += 0.3
                    else:  # Larger leaps
                        score += 0.1
                
                prev_pitch = pitch
        
        return score / intervals if intervals > 0 else 0.5
    
    def _arpeggio_scale_mix(self, genome: MelodyGenome) -> float:
        """
        Evaluate mixture of arpeggiated and scalar motion.
        
        
        Checks for patterns that combine skips (arpeggios) with steps (scales).
        The point is to reward the classic "arpeggiate up, scale down" pattern.
        
        
        Usually jazz melodies balance vertical energy (arpeggios) with horizontal
        lyricism (scales). Arpeggios outline the harmony explicitly while scales.
        
        Returns:
            Score between 0 and 1
        """
        skip_count = 0
        step_count = 0
        arp_up_scale_down = 0
        patterns = 0
        
        pitches = [p for p in genome.pitches if p != REST]
        
        if len(pitches) < 4:
            return 0.5
        
        for i in range(1, len(pitches)):
            interval = abs(pitches[i] - pitches[i-1])
            if interval <= 2:
                step_count += 1
            elif interval >= 3:
                skip_count += 1
        
        # Look for "arpeggio up, scale down" patterns
        for i in range(len(pitches) - 3):
            p1, p2, p3, p4 = pitches[i:i+4]
            
            # Skip up (3+ semitones), then steps down
            if p2 > p1 and (p2 - p1) >= 3:  # Skip up
                if p3 < p2 and (p2 - p3) <= 2:  # Step down
                    if p4 < p3 and (p3 - p4) <= 2:  # Another step down
                        arp_up_scale_down += 1
            patterns += 1
        
        # Calculate scores
        total_movements = step_count + skip_count
        if total_movements == 0:
            return 0.5
        
        # Ideal ratio: about 60% steps, 40% skips
        step_ratio = step_count / total_movements
        ratio_score = 1.0 - abs(0.6 - step_ratio) * 2  # Peaks at 60%
        ratio_score = max(0, ratio_score)
        
        # Bonus for arpeggio-scale patterns
        pattern_score = min(1.0, arp_up_scale_down / max(patterns // 4, 1))
        
        return 0.6 * ratio_score + 0.4 * pattern_score
    
    def _phrase_contour(self, genome: MelodyGenome) -> float:
        """
        Evaluate phrase-level melodic contour.
        
        Analyzes the overall shape of the melody across phrases (2-bar groups),
        rewarding melodies that have clear directional motion and avoiding
        excessive randomness. Jazz phrases typically have coherent shapes,
        creating musical tension and release.
        
        Returns:
            Score between 0 and 1
        """
        phrase_scores = []
        
        for phrase_idx in range(4):
            start_bar = phrase_idx * 2
            phrase_pitches = []
            
            for bar_idx in range(start_bar, start_bar + 2):
                phrase_pitches.extend(genome.get_bar(bar_idx))
            
            actual_pitches = [p for p in phrase_pitches if p != REST]
            
            if len(actual_pitches) < 3:
                phrase_scores.append(0.5)
                continue
            
            # Calculate direction changes
            direction_changes = 0
            for i in range(1, len(actual_pitches) - 1):
                prev_dir = actual_pitches[i] - actual_pitches[i-1]
                next_dir = actual_pitches[i+1] - actual_pitches[i]
                
                if (prev_dir > 0 and next_dir < 0) or \
                   (prev_dir < 0 and next_dir > 0):
                    direction_changes += 1
            
            # Fewer direction changes = more coherent contour
            max_changes = len(actual_pitches) - 2
            if max_changes > 0:
                change_ratio = direction_changes / max_changes
                if change_ratio <= 0.3:
                    phrase_scores.append(0.8 + change_ratio * 0.67)
                elif change_ratio <= 0.5:
                    phrase_scores.append(1.0 - (change_ratio - 0.3) * 2)
                else:
                    phrase_scores.append(max(0, 0.6 - (change_ratio - 0.5)))
            else:
                phrase_scores.append(0.5)
        
        return sum(phrase_scores) / len(phrase_scores) if phrase_scores else 0.5
    
    def _note_density(self, genome: MelodyGenome) -> float:
        """
        Evaluate appropriate note density (not too sparse, not too busy).
        
        Measures the ratio of notes to rests, rewarding melodies that have
        a balanced density. Jazz melodies need space to breathe but also
        enough notes to maintain interest. Target density: 50-75% notes.
        
        Returns:
            Score between 0 and 1
        """
        from src.core import TOTAL_NOTES
        
        note_count = sum(1 for p in genome.pitches if p != REST)
        density = note_count / TOTAL_NOTES
        
        if density < 0.3:
            return density / 0.3 * 0.5  # Too sparse
        elif density <= 0.5:
            return 0.5 + (density - 0.3) / 0.2 * 0.5
        elif density <= 0.75:
            return 1.0  # Optimal range
        else:
            return max(0.3, 1.0 - (density - 0.75) * 3)  # Too dense
    
    def _range_fitness(self, genome: MelodyGenome) -> float:
        """
        Evaluate if melody stays within a playable/singable range.
        
        Checks if the melody stays within a reasonable range (roughly an
        octave to an octave and a half). This ensures the melody is practical
        for vocalists and instrumentalists.
        
        Returns:
            Score between 0 and 1
        """
        pitches = [p for p in genome.pitches if p != REST]
        
        if not pitches:
            return 0
        
        min_pitch = min(pitches)
        max_pitch = max(pitches)
        range_size = max_pitch - min_pitch
        
        # Ideal range is 12-18 semitones (octave to octave and a half)
        if range_size < 8:
            return 0.5 + range_size / 16  # Too narrow
        elif range_size <= 18:
            return 1.0  # Optimal
        else:
            return max(0.3, 1.0 - (range_size - 18) / 24)  # Too wide
