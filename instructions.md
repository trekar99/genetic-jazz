# Assignment 1: Genetic Jazz Melody Generator

Hey Team,

Great work on the previous genetic algorithm assignment — you’ve already proven that you can make evolutionary systems *behave musically*. Now it’s time to raise the bar and step fully into jazz territory. 🎷

This time, we flip the problem.

Instead of harmonizing a melody, your system will generate a melody that fits a given jazz chord progression.

## Mission

Design and implement a genetic algorithm that generates a melodic line over a predefined 8-bar jazz chord progression, under the following constraints:

* 8 bars, 4/4
* 1 chord per bar
* All chords are 7th chords (e.g. maj7, min7, dom7, half-diminished, etc.)
* The chord progression is given and fixed
* The melody must be stylistically and harmonically compatible with the progression

Think lead sheet *jazz melody*, not classical counterpoint.

## High-Level Goal

Your task is to evolve melodies that:
* Outline the underlying harmony
* Use musically meaningful chord tones and tensions
* Exhibit good melodic motion and phrasing
* Sound plausible as a jazz melody (even if simple)

## Team Roles & Tasks

As before, I strongly recommend splitting responsibilities.

### 1. Jazz-Aware Fitness Metrics

Design fitness functions that evaluate how well a melody fits a jazz chord progression.

Examples (you don’t need to implement any of these):

* Emphasis on chord tones on strong beats
* Controlled use of tensions (9ths, 11ths, 13ths)
* Penalization of “wrong” notes against the chord
* Stepwise melodic motion vs. excessive leaps
* Motivic consistency across bars
* Phrase-level contour (e.g. avoiding randomness)

Each metric should reflect a musical intuition.

### 2. Melody Representation
Decide how a melody is encoded genetically. For example:
* Notes per bar
* Pitch + duration genes
* Fixed rhythmic grid vs. evolving rhythm

Keep it simple but meaningful.

### 3. Genetic Algorithm Design

Adapt the GA from the previous implementation to this new task.

You are free to:
* Keep parts of the old fitness functions
* Modify them
* Remove them entirely

Justify your choices musically and technically.

## Chord Progression
You may:

* Use a provided jazz progression (e.g. ii–V–I variants), or
* Define your own 8-bar progression, as long as:
  * It contains only 7th chords
  * 1 chord per bar
  * It is clearly documented in the code

The system should be able to receive a chord progression with the characteristics above as input.

The chord progression must remain fixed during evolution.

## Deliverables
### 1. Working Code & MIDI Output
* The code must run end-to-end
* The system must generate a melody over the given chord progression
* the result should be exported as a MIDI file
* The MIDI should be readable in notation software (e.g. MuseScore)

### 2. Fitness Metric Documentation
For each fitness metric, include:

* A short docstring explaining:
  * What it evaluates
  * Why it matters musically (in a jazz context)

### 3. Presentation

Depending on the number of teams, you may be asked to present your work in class
* 5-minute presentation (prepare slides)
  * What have you done?
  * How?
* Be ready with a MIDI rendering, and a score of one of the outputs of your system. We’ll try to play the output in class with live musicians. If not, we’ll fall back to the MIDI.

## Deadlines
* The assignment is due by **February 15th** at midnight on GitHub Classroom
* Your team will (possibly) present on February 16th in class

## Final Notes

This assignment is deliberately open-ended.

There is no single “correct” jazz melody — what matters is whether:

* Your system encodes musical reasoning
* Your fitness functions make aesthetic sense
* The results improve over generations

Experiment, listen critically, and trust your musical intuition.

Let’s see if your algorithms can swing. 😉

Good luck!

Your CTO, Valerio

---
