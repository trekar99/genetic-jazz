"""
Flask web application for the Genetic Jazz Melody Generator.

This module provides a web interface to:
- Browse available jazz standards from the data folder
- Generate melodies using the genetic algorithm
- View generated sheet music and play MIDI audio
"""

import sys
from pathlib import Path

# Add parent directory to path for imports when running from src/
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import glob
import base64

from flask import Flask, render_template, jsonify, request, send_file

from src.genetic import JazzFitnessEvaluator, GeneticJazzMelodyGenerator, FITNESS_WEIGHTS_CONFIG, get_default_weights
from src.progressions import get_progression_from_xml
from src.utils import create_jazz_score, export_to_midi, export_to_png
from src.core import ChordProgression, ChordFactory

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Path to data folder
DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'output')

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def get_available_songs():
    """Get list of available XML files from data folder."""
    xml_files = glob.glob(os.path.join(DATA_FOLDER, '*.xml'))
    songs = []
    for f in sorted(xml_files):
        name = os.path.basename(f).replace('.xml', '')
        songs.append({'name': name, 'path': f})
    return songs


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/songs')
def list_songs():
    """API endpoint to list available songs."""
    songs = get_available_songs()
    return jsonify({'songs': [s['name'] for s in songs]})


@app.route('/api/fitness-config')
def get_fitness_config():
    """API endpoint to get fitness weights configuration."""
    return jsonify({'weights': FITNESS_WEIGHTS_CONFIG})


@app.route('/api/generate', methods=['POST'])
def generate_melody():
    """API endpoint to generate a melody for a selected song or custom progression."""
    data = request.json
    mode = data.get('mode', 'song')
    generations = data.get('generations', 1000)
    
    try:
        if mode == 'custom':
            # Handle custom chord progression
            chords_data = data.get('chords', [])
            progression_name = data.get('progression_name', 'Custom Progression')
            
            if not chords_data or len(chords_data) != 8:
                return jsonify({'error': 'Custom progression must have exactly 8 chords'}), 400
            
            # Create JazzChord objects from the chord data
            chords = []
            for chord_info in chords_data:
                root = chord_info.get('root')
                quality = chord_info.get('quality')
                try:
                    chord = ChordFactory.create(root, quality)
                    chords.append(chord)
                except ValueError as e:
                    return jsonify({'error': f'Invalid chord: {root}{quality} - {str(e)}'}), 400
            
            progression = ChordProgression(chords=chords, name=progression_name)
        else:
            # Handle song selection mode
            song_name = data.get('song')
            if not song_name:
                return jsonify({'error': 'No song selected'}), 400
            
            # Find the XML file
            xml_path = os.path.join(DATA_FOLDER, f'{song_name}.xml')
            if not os.path.exists(xml_path):
                return jsonify({'error': f'Song not found: {song_name}'}), 404
            
            # Load chord progression
            progression = get_progression_from_xml(xml_path)
        
        # Get chord names for display
        chord_names = [chord.name for chord in progression.chords]
        
        # Setup fitness evaluator using centralized config
        default_weights = get_default_weights()
        incoming_weights = data.get('weights') or {}
        weights = {}
        for key, default_value in default_weights.items():
            try:
                weights[key] = float(incoming_weights.get(key, default_value))
            except (TypeError, ValueError):
                weights[key] = default_value

        default_numeric_params = {
            'population_size': 100,
            'mutation_rate': 0.15,
            'elite_size': 5
        }
        default_string_params = {
            'pairing_strategy': 'random'
        }
        fitness_evaluator = JazzFitnessEvaluator(
            progression=progression,
            weights=weights
        )
        
        incoming_params = data.get('params') or {}
        params = {}
        for key, default_value in default_numeric_params.items():
            try:
                params[key] = float(incoming_params.get(key, default_value))
            except (TypeError, ValueError):
                params[key] = default_value
        for key, default_value in default_string_params.items():
            incoming_value = incoming_params.get(key, default_value)
            if incoming_value is None:
                params[key] = default_value
            else:
                params[key] = str(incoming_value)
        
        # Setup genetic algorithm
        generator = GeneticJazzMelodyGenerator(
            progression=progression,
            fitness_evaluator=fitness_evaluator,
            population_size=int(params['population_size']),
            mutation_rate=params['mutation_rate'],
            elite_size=int(params['elite_size']),
            pairing_strategy=params['pairing_strategy']
        )
        
        # Generate melody
        best_melody = generator.generate(generations=generations)
        final_fitness = fitness_evaluator.evaluate(best_melody)
        
        # Create score
        score = create_jazz_score(best_melody, progression)
        
        # Export MIDI
        safe_name = progression.name.replace(' ', '_').replace("'", "").replace("(", "").replace(")", "")
        midi_filename = f"generated_{safe_name}.mid"
        midi_path = os.path.join(OUTPUT_FOLDER, midi_filename)
        export_to_midi(score, midi_path)
        
        # Export sheet music as PNG
        png_filename = f"generated_{safe_name}"
        png_path = os.path.join(OUTPUT_FOLDER, png_filename)
        try:
            actual_png_path = export_to_png(score, png_path)
            # Read PNG and encode as base64
            with open(actual_png_path, 'rb') as f:
                sheet_base64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Warning: Could not generate sheet music image: {e}")
            sheet_base64 = None
        
        # Read MIDI file and encode as base64 for browser playback
        with open(midi_path, 'rb') as f:
            midi_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'song_name': progression.name,
            'chords': chord_names,
            'fitness_score': round(final_fitness, 4),
            'midi_base64': midi_base64,
            'midi_filename': midi_filename,
            'sheet_base64': sheet_base64
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_midi(filename):
    """Download a generated MIDI file."""
    midi_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(midi_path):
        return send_file(midi_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    print("Starting Genetic Jazz Melody Generator Web App...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
