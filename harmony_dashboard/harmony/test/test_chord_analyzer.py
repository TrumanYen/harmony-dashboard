import pytest
import pretty_midi
import random

from ...harmony_domain import ChordType, ScaleAgnosticChord
from ..chord_analyzer import ChordAnalyzer


def pitch_at_random_octave(note_name: str):
    octave = random.randint(1, 7)
    return pretty_midi.note_name_to_number(note_name + str(octave))


class TestChordAnalyzer:

    @pytest.fixture(autouse=True)
    def before_each_test(self):
        self.patient = ChordAnalyzer()

    def test_will_return_no_chord_if_no_pitches_received(self):
        empty_pitch_list = []

        actual_chord, _ = self.patient.analyze_chord(empty_pitch_list)

        expected_chord = None
        assert actual_chord == expected_chord

    @staticmethod
    def will_return_empty_chord_given_insufficient_pitches_data():
        no_pitches = []
        one_pitch = [pitch_at_random_octave("C")]
        two_of_same_note = [
            pretty_midi.note_name_to_number("C2"),
            pretty_midi.note_name_to_number("C3"),
        ]

        return [
            pytest.param(no_pitches),
            pytest.param(one_pitch),
            pytest.param(two_of_same_note),
        ]

    @pytest.mark.parametrize(
        "pitch_list", will_return_empty_chord_given_insufficient_pitches_data()
    )
    def test_will_return_empty_chord_given_insufficient_pitches(
        self, pitch_list: list[int]
    ):
        expected_current_chord = None

        actual_current_chord, _ = self.patient.analyze_chord(pitch_list)
        assert expected_current_chord == actual_current_chord

    @staticmethod
    def will_identify_all_inversions_of_g_major_triad_data():
        root_position = [
            pretty_midi.note_name_to_number("G3"),
            pretty_midi.note_name_to_number("B3"),
            pretty_midi.note_name_to_number("D4"),
        ]
        first_inversion = [
            pretty_midi.note_name_to_number("B3"),
            pretty_midi.note_name_to_number("D4"),
            pretty_midi.note_name_to_number("G4"),
        ]
        second_inversion = [
            pretty_midi.note_name_to_number("D4"),
            pretty_midi.note_name_to_number("G4"),
            pretty_midi.note_name_to_number("B4"),
        ]
        return [
            pytest.param(root_position),
            pytest.param(first_inversion),
            pytest.param(second_inversion),
        ]

    @pytest.mark.parametrize(
        "g_maj_pitch_list", will_identify_all_inversions_of_g_major_triad_data()
    )
    def test_will_identify_all_inversions_of_g_major_triad(self, g_maj_pitch_list):
        expected_chord = ScaleAgnosticChord(
            root_wrapped_pitch=10, chord_type=ChordType.MAJOR
        )

        actual_chord, _ = self.patient.analyze_chord(g_maj_pitch_list)

        assert actual_chord == expected_chord

    @staticmethod
    def will_identify_various_complete_chords_data():
        # MINOR TRIAD
        f_minor_pitches = [
            pitch_at_random_octave("F"),
            pitch_at_random_octave("Ab"),
            pitch_at_random_octave("C"),
        ]
        f_minor_chord = ScaleAgnosticChord(
            root_wrapped_pitch=8, chord_type=ChordType.MINOR
        )

        # SEVENTH CHORD
        a_dom_seventh_pitches = [
            pitch_at_random_octave("A"),
            pitch_at_random_octave("C#"),
            pitch_at_random_octave("E"),
            pitch_at_random_octave("G"),
        ]
        a_dom_seventh_chord = ScaleAgnosticChord(
            root_wrapped_pitch=0, chord_type=ChordType.SEVENTH
        )

        # MAJ SEVENTH CHORD
        g_maj_seventh_pitches = [
            pitch_at_random_octave("G"),
            pitch_at_random_octave("B"),
            pitch_at_random_octave("D"),
            pitch_at_random_octave("F#"),
        ]
        g_maj_seventh_chord = ScaleAgnosticChord(
            root_wrapped_pitch=10, chord_type=ChordType.MAJ_SEVENTH
        )

        # MIN SEVENTH CHORD
        d_min_seventh_pitches = [
            pitch_at_random_octave("D"),
            pitch_at_random_octave("F"),
            pitch_at_random_octave("A"),
            pitch_at_random_octave("C"),
        ]
        d_min_seventh_chord = ScaleAgnosticChord(
            root_wrapped_pitch=5, chord_type=ChordType.MIN_SEVENTH
        )

        # DIM TRIAD
        # Dim chords look the same in each inversion so we need to specify the octaves here
        b_dim_pitches = [
            pretty_midi.note_name_to_number("B3"),
            pretty_midi.note_name_to_number("D4"),
            pretty_midi.note_name_to_number("F4"),
        ]
        b_dim_chord = ScaleAgnosticChord(
            root_wrapped_pitch=2, chord_type=ChordType.DIMINISHED
        )

        # DIM SEVENTH
        # Dim chords look the same in each inversion so we need to specify the octaves here
        c_sharp_dim_seventh_pitches = [
            pretty_midi.note_name_to_number("C#4"),
            pretty_midi.note_name_to_number("E4"),
            pretty_midi.note_name_to_number("G4"),
            pretty_midi.note_name_to_number("A#4"),
        ]
        c_sharp_dim_seventh_chord = ScaleAgnosticChord(
            root_wrapped_pitch=4, chord_type=ChordType.DIM_SEVENTH
        )

        return [
            pytest.param(f_minor_pitches, f_minor_chord),
            pytest.param(a_dom_seventh_pitches, a_dom_seventh_chord),
            pytest.param(g_maj_seventh_pitches, g_maj_seventh_chord),
            pytest.param(d_min_seventh_pitches, d_min_seventh_chord),
            pytest.param(b_dim_pitches, b_dim_chord),
            pytest.param(c_sharp_dim_seventh_pitches, c_sharp_dim_seventh_chord),
        ]

    @pytest.mark.parametrize(
        "pitch_list, expected_chord", will_identify_various_complete_chords_data()
    )
    def test_will_identify_various_complete_chords(
        self, pitch_list: list[int], expected_chord: ScaleAgnosticChord
    ):
        actual_chord, _ = self.patient.analyze_chord(pitch_list)

        assert actual_chord == expected_chord
