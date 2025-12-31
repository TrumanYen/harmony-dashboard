import pytest

from harmony_domain import Note, NoteName, Chord, ChordType, ScaleAgnosticChord
from enharmonic_resolver import EnharmonicResolver


class TestEnharmonicResolver:

    @pytest.fixture(autouse=True)
    def before_each_test(self):
        self.patient = EnharmonicResolver()

    @staticmethod
    def will_select_key_signature_with_least_sharps_or_flats_data():
        return [
            pytest.param(2, Note(NoteName.B, 0)),
            pytest.param(4, Note(NoteName.D, -1)),
        ]

    @pytest.mark.parametrize(
        "tonal_center_pitch, expected_scale",
        will_select_key_signature_with_least_sharps_or_flats_data(),
    )
    def test_will_select_key_signature_with_least_sharps_or_flats(
        self, tonal_center_pitch: int, expected_scale: Note
    ):
        arbitrary_chord = ScaleAgnosticChord(0, ChordType.MAJOR)
        empty_pitch_list = []
        harmony_state = self.patient.convert_from_wrapped_pitches_to_notes(
            tonal_center_pitch, arbitrary_chord, empty_pitch_list
        )

        assert harmony_state.current_major_scale == expected_scale

    def test_will_select_chord_in_scale_if_possible(self):
        wrapped_pitch_for_e_flat = 6
        b_flat_chord = ScaleAgnosticChord(
            root_wrapped_pitch=1, chord_type=ChordType.MAJOR
        )
        expected_chord = Chord(
            root=Note(note_name=NoteName.B, accidentals=-1), chord_type=ChordType.MAJOR
        )

        harmony_state = self.patient.convert_from_wrapped_pitches_to_notes(
            current_tonal_center_wrapped_pitch=wrapped_pitch_for_e_flat,
            current_chord=b_flat_chord,
            detected_notes_wrapped_pitches=[],
        )

        assert harmony_state.current_chord == expected_chord

    def test_will_select_closest_chord_to_last_if_not_in_scale(self):
        wrapped_pitch_for_g = 10
        f_sharp_chord = ScaleAgnosticChord(
            root_wrapped_pitch=9, chord_type=ChordType.DIM_SEVENTH
        )
        c_sharp_chord = ScaleAgnosticChord(
            root_wrapped_pitch=4, chord_type=ChordType.MINOR
        )  # Not in the g major scale, but most likely to be C# rather than Db
        # since we were in f sharp dim last chord
        expected_chord = Chord(
            root=Note(note_name=NoteName.C, accidentals=1), chord_type=ChordType.MINOR
        )

        self.patient.convert_from_wrapped_pitches_to_notes(
            current_tonal_center_wrapped_pitch=wrapped_pitch_for_g,
            current_chord=f_sharp_chord,
            detected_notes_wrapped_pitches=[],
        )
        new_harmony_state = self.patient.convert_from_wrapped_pitches_to_notes(
            current_tonal_center_wrapped_pitch=wrapped_pitch_for_g,
            current_chord=c_sharp_chord,
            detected_notes_wrapped_pitches=[],
        )

        assert new_harmony_state.current_chord == expected_chord

    def test_will_apply_key_signature_to_notes_if_in_scale(self):
        wrapped_pitch_for_a = 0
        a_chord = ScaleAgnosticChord(root_wrapped_pitch=0, chord_type=ChordType.MAJOR)
        pitches_in_a = [0, 2, 4, 5, 7, 9, 11]
        expected_notes = [
            Note(NoteName.A, 0),
            Note(NoteName.B, 0),
            Note(NoteName.C, 1),
            Note(NoteName.D, 0),
            Note(NoteName.E, 0),
            Note(NoteName.F, 1),
            Note(NoteName.G, 1),
        ]

        harmony_state = self.patient.convert_from_wrapped_pitches_to_notes(
            current_tonal_center_wrapped_pitch=wrapped_pitch_for_a,
            current_chord=a_chord,
            detected_notes_wrapped_pitches=pitches_in_a,
        )

        assert harmony_state.notes_detected == expected_notes

    def test_will_apply_accidentals_to_notes_based_on_chord_if_not_in_scale(self):
        wrapped_pitch_for_c = 3
        e_chord = ScaleAgnosticChord(root_wrapped_pitch=7, chord_type=ChordType.MAJOR)
        pitches_outside_c = [11]  # G# is in the e chord but not part of C major
        expected_notes = [
            Note(NoteName.G, 1),
        ]

        harmony_state = self.patient.convert_from_wrapped_pitches_to_notes(
            current_tonal_center_wrapped_pitch=wrapped_pitch_for_c,
            current_chord=e_chord,
            detected_notes_wrapped_pitches=pitches_outside_c,
        )

        assert harmony_state.notes_detected == expected_notes
