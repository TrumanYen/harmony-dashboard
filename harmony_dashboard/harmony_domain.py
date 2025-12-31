from enum import Enum, auto
from dataclasses import dataclass


class NoteName(Enum):
    A = auto()
    B = auto()
    C = auto()
    D = auto()
    E = auto()
    F = auto()
    G = auto()


@dataclass
class Note:
    """
    Musical note, octave-agnostic.

    'accidentals' is in semitones.  (e.g. 0=natural, 1=sharp, -1=flat, -2=double flat, etc.)
    """

    note_name: NoteName
    accidentals: int


class ChordType(Enum):
    """
    There are only 6 actual chords, the rest are mental disorders.
    """

    MAJOR = auto()
    MINOR = auto()
    DIMINISHED = auto()
    SEVENTH = auto()
    MIN_SEVENTH = auto()
    DIM_SEVENTH = auto()


@dataclass
class Chord:
    root: Note
    chord_type: ChordType


@dataclass
class HarmonyState:
    """
    Note that not all notes detected necessarily belong in a chord,
    and not all canonical notes in the chord were necessarily detected.

    'current_chord' and 'notes_detected' both may be None.
    """

    current_major_scale: Note | None
    current_chord: Chord | None
    notes_detected: list[Note] | None


@dataclass
class ScaleAgnosticChord:
    """
    Chord agnostic of enharmonic equivalents or octave.
    For example, a major chord with a root of B2 and a major chord
    with a root of Cb4 would both have 'root_wrapped_pitch'=2
    and 'chord_type'=ChordType.MAJOR
    """

    root_wrapped_pitch: int
    chord_type: ChordType
