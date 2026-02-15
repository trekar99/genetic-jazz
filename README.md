# Genetic Jazz Melody Generator

A genetic algorithm-based system for generating jazz melodies over chord progressions. The system evolves melodies that fit harmonically with the underlying chords while maintaining musical characteristics such as smooth melodic motion, appropriate phrase contour, and balanced note density.

## Features

- **Genetic Algorithm Melody Generation**: Evolves melodies using selection, crossover, and mutation operators tailored for musical applications
- **Jazz-Specific Fitness Evaluation**: Multi-weighted fitness function evaluating chord tone emphasis, tension usage, melodic motion, phrase contour, and more
- **MusicXML Import**: Parse chord progressions from iRealPro-compatible MusicXML files
- **MIDI Export**: Export generated melodies as MIDI files for playback in any DAW or notation software
- **Web Interface**: Browser-based demo application for selecting songs and generating melodies
- **Sheet Music Display**: Visual score rendering using Music21 (requires MuseScore)

## Project Structure

```
genetic-jazz-sonabe/
├── src/
│   ├── core/                    # Core data structures
│   │   ├── constants.py         # MIDI, rhythmic, and structure constants
│   │   ├── chorddata.py         # JazzChord, ChordProgression, MelodyGenome
│   │   └── chordfactory.py      # Factory for creating jazz chords
│   ├── genetic/                 # Genetic algorithm components
│   │   ├── fitness.py           # JazzFitnessEvaluator
│   │   └── generator.py         # GeneticJazzMelodyGenerator
│   ├── progressions/            # Chord progression sources
│   │   ├── presets.py           # Common jazz progressions (ii-V-I, etc.)
│   │   └── xmlparser.py         # MusicXML parser for iRealPro files
│   ├── main.py                  # Command-line entry point
│   ├── webapp.py                # Flask web application
│   └── utils.py                 # Score creation and export utilities
├── data/                        # MusicXML chord progression files
├── templates/                   # HTML templates for web interface
├── output/                      # Generated MIDI and PNG files
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.10 or higher
- MuseScore (optional, for sheet music PNG export)

### Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd genetic-jazz-sonabe
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Install MuseScore for sheet music rendering:

   ```bash
   # Ubuntu/Debian
   sudo apt install musescore
   
   # macOS (Homebrew)
   brew install musescore
   
   # Windows: Download from https://musescore.org
   ```

   Note: Music21 looks for MuseScore3 at `/usr/bin/mscore3`. If your installation places the binary at `/usr/bin/mscore`, create a symlink:

   ```bash
   sudo ln -s /usr/bin/mscore /usr/bin/mscore3
   ```

## Usage

### Command Line

Run the main script to generate a melody:

```bash
cd src
python main.py
```

This will:

1. Load a chord progression from the data folder
2. Configure the fitness evaluator and genetic algorithm
3. Evolve a melody over 1000 generations
4. Export the result to `generated_jazz_melody.mid`
5. Optionally display the score (if Music21 viewer is configured)

### Web Interface

Start the Flask development server:

```bash
cd src
python webapp.py
```

Then open <http://localhost:5000> in your browser to:

- Search and select from available jazz standards
- Configure the number of generations
- Generate melodies and view fitness scores
- Play back generated melodies in the browser
- Download MIDI files
- View sheet music (if MuseScore is installed)

## Configuration

### Fitness Weights

The fitness evaluator uses weighted metrics to guide melody evolution. Default weights can be customized in the web interface:

| Metric | Default Weight | Description |
|--------|---------------|-------------|
| `chord_tone_emphasis` | 0.15 | Chord tones on strong beats |
| `tension_usage` | 0.15 | Controlled use of 9ths, 11ths, 13ths |
| `avoid_wrong_notes` | 0.15 | Penalize clashing notes |
| `call_and_response` | 0.15 | Reward call and response patterns |
| `melodic_motion` | 0.10 | Prefer stepwise motion and leaps |
| `arpeggio_scale_mix` | 0.05 | reward a mix of arpeggiated motion |
| `phrase_contour` | 0.10 | Coherent melodic shapes |
| `note_density` | 0.05 | Balanced note/rest ratio |
| `range_fitness` | 0.05 | Stay in playable range |

### Adding or Removing Fitness Functions

All fitness function configuration is centralized in a single file: `src/genetic/fitness.py`.

#### To Add a New Fitness Function

1. **Add an entry to `FITNESS_WEIGHTS_CONFIG`** at the top of `fitness.py`:

   ```python
   FITNESS_WEIGHTS_CONFIG = [
       # ... existing entries ...
       {
           'key': 'your_new_function',      # Internal key (must match method name)
           'label': 'Your New Function',    # Display name in web UI
           'default': 0.10,                 # Default weight (0.0 to 1.0)
           'description': 'What this function measures'  # Tooltip text
       },
   ]
   ```

2. **Implement the corresponding method** in the `JazzFitnessEvaluator` class:

   ```python
   def _your_new_function(self, genome: MelodyGenome) -> float:
       """
       Evaluate your custom metric.
       
       Args:
           genome: The melody genome to evaluate
           
       Returns:
           Float between 0 and 1 (higher is better)
       """
       # Your implementation here
       score = 0.0
       # ... calculate score ...
       return score
   ```

That's it! The web interface will automatically:

- Generate a slider for the new parameter
- Include it in the fitness calculation
- Normalize weights to sum to 1.0

#### To Remove a Fitness Function

1. Delete the entry from `FITNESS_WEIGHTS_CONFIG`
2. Delete the corresponding `_function_name()` method

The web interface will automatically update on the next page load.

### Genetic Algorithm Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `population_size` | 100 | Number of genomes per generation |
| `mutation_rate` | 0.15 | Probability of mutation per genome |
| `elite_size` | 5 | Number of top genomes preserved |
| `pairing_strategy` | `random` | Parent pairing strategy (`random`, `similarity`, `dissimilarity`, `best_first_last`) |
| `generations` | 500-1000 | Number of evolution cycles |

#### Pairing Strategies

| Strategy | Description |
|----------|-------------|
| `random` | Uniform random parent pairing |
| `similarity` | Pair a parent with its most similar mate |
| `dissimilarity` | Pair a parent with its most dissimilar mate |
| `best_first_last` | Pair a high-fitness parent with a low-fitness parent |

## Supported Chord Types

The system supports common jazz chord types:

- **Major**: maj7
- **Minor**: min7
- **Dominant**: dom7, dom7#11
- **Half-Diminished**: min7b5
- **Diminished**: dim7
- **Minor-Major**: minMaj7
- **Augmented**: maj7#5
- **Suspended**: 7sus4

## Adding New Progressions

### From MusicXML

Place MusicXML files in the `data/` folder. The parser extracts the first 8 bars with one chord per bar.

### Programmatically

```python
from src.core import ChordProgression, ChordFactory

chords = [
    ChordFactory.create("D", "min7"),
    ChordFactory.create("G", "dom7"),
    ChordFactory.create("C", "maj7"),
    # ... add 8 chords total
]
progression = ChordProgression(chords=chords, name="My Progression")
```

## Technical Details

### Melody Representation

Melodies are encoded as fixed-grid sequences of MIDI pitches:

- 8 bars, 8 eighth-note slots per bar (64 total slots)
- Each slot contains a MIDI pitch (60-84) or REST (-1)
- Range: C4 to C6 (two octaves)

### Genetic Operators

- **Selection**: Fitness-proportionate (roulette wheel)
- **Crossover**: One-point at bar boundaries to preserve phrase coherence
- **Mutation**: Random pitch change, chord tone snap, or rest toggle

### Dependencies

- **music21**: Score creation, MIDI export, notation rendering
- **Flask**: Web application framework

## License

This project is part of coursework for the Sound and Music Computing Master's program.

## Acknowledgments

- Jazz chord progressions sourced from iRealPro
- Built with Music21 by MIT
