import pytest
import pretty_midi
from unittest.mock import Mock
import random

from harmony_domain import NoteName, Note, ChordType, Chord, HarmonyState
from app import I_HarmonyStateListener
from harmony_analyzer import HarmonyAnalyzer


def pitch_at_random_octave(note_name: str):
    octave = random.randint(1, 7)
    return pretty_midi.note_name_to_number(note_name + str(octave))


class TestHarmonyAnalyzer:
    def harmony_state_received_by_listener(self) -> HarmonyState:
        return self.listener.update_harmony_state.call_args.args[0]

    @pytest.fixture(autouse=True)
    def before_each_test(self):
        self.listener = Mock(spec=I_HarmonyStateListener)
        self.patient = HarmonyAnalyzer()
        self.patient.register_listener(self.listener)

    def test_will_not_send_harmony_state_if_no_pitches_received(self):
        empty_pitch_list = []

        self.patient.new_pitches_detected(empty_pitch_list)

        self.listener.update_harmony_state.assert_not_called()

    def test_will_return_all_detected_notes_with_default_key_signature_if_no_scale_detected(
        self,
    ):
        pitch_list = [
            pitch_at_random_octave("C"),
            pitch_at_random_octave("D"),
            pitch_at_random_octave("E"),
            pitch_at_random_octave("G"),
        ]

        self.patient.new_pitches_detected(pitch_list)

        expected_notes_detected = [
            Note(NoteName.C, 0),
            Note(NoteName.D, 0),
            Note(NoteName.E, 0),
            Note(NoteName.G, 0),
        ]
        actual_notes_detected = self.harmony_state_received_by_listener().notes_detected
        for note in expected_notes_detected:
            assert note in actual_notes_detected
        assert len(expected_notes_detected) == len(actual_notes_detected)

    def test_will_not_return_duplicate_notes(self):
        pitch_list = [
            pretty_midi.note_name_to_number("C1"),
            pretty_midi.note_name_to_number("C2"),
        ]

        self.patient.new_pitches_detected(pitch_list)

        expected_notes_detected = [
            Note(NoteName.C, 0),
        ]
        actual_notes_detected = self.harmony_state_received_by_listener().notes_detected
        for note in expected_notes_detected:
            assert note in actual_notes_detected
        assert len(expected_notes_detected) == len(actual_notes_detected)

    def test_will_return_correct_chord_with_no_default_key_signature_if_no_scale_detected(
        self,
    ):
        f_seventh_chord_pitches = [
            pitch_at_random_octave("F"),
            pitch_at_random_octave("A"),
            pitch_at_random_octave("C"),
            pitch_at_random_octave("Eb"),
        ]

        self.patient.new_pitches_detected(f_seventh_chord_pitches)

        expected_chord = Chord(
            root=Note(note_name=NoteName.F, accidentals=0), chord_type=ChordType.SEVENTH
        )
        actual_chord_detected = self.harmony_state_received_by_listener().current_chord
        assert expected_chord == actual_chord_detected
