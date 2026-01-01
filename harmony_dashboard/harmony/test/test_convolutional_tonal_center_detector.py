import pytest

from ...harmony_domain import ScaleAgnosticChord, ChordType
from ..tonal_center_detector import ConvolutionalTonalCenterDetector


class TestConvolutionalTonalCenterDetector:
    @pytest.fixture(autouse=True)
    def before_each_test(self):
        self.patient = ConvolutionalTonalCenterDetector()

    def test_can_predict_obviously_c_major_progression(self):
        chord_progression = self.very_obviously_c_major_progression()
        for chord in chord_progression:
            self.patient.insert_chord(chord)
        expected_tonal_center = 3  # C major

        actual_tonal_center = self.patient.predict_tonal_center()

        assert actual_tonal_center == expected_tonal_center

    def test_can_change_tonal_center(self):
        c_major_progression = self.very_obviously_c_major_progression()
        for chord in c_major_progression:
            self.patient.insert_chord(chord)
        for chord in c_major_progression:
            self.patient.remove_chord(chord)
        d_major_progression = self.very_obviously_d_major_progression()
        for chord in d_major_progression:
            self.patient.insert_chord(chord)

        expected_tonal_center = 5  # D major

        actual_tonal_center = self.patient.predict_tonal_center()

        assert actual_tonal_center == expected_tonal_center

    def test_removing_more_chords_than_present_is_benign(self):
        c_major_progression = self.very_obviously_c_major_progression()
        for chord in c_major_progression:
            self.patient.remove_chord(chord)
            self.patient.remove_chord(chord)
            self.patient.insert_chord(chord)
        expected_tonal_center = 3  # C major

        actual_tonal_center = self.patient.predict_tonal_center()

        assert actual_tonal_center == expected_tonal_center

    # Helpers
    def very_obviously_c_major_progression(self):
        return [
            ScaleAgnosticChord(root_wrapped_pitch=3, chord_type=ChordType.MAJOR),  # C
            ScaleAgnosticChord(root_wrapped_pitch=10, chord_type=ChordType.MAJOR),  # G
            ScaleAgnosticChord(root_wrapped_pitch=3, chord_type=ChordType.MAJOR),  # C
            ScaleAgnosticChord(root_wrapped_pitch=8, chord_type=ChordType.MAJOR),  # F
            ScaleAgnosticChord(
                root_wrapped_pitch=2, chord_type=ChordType.DIM_SEVENTH
            ),  # B dim7
            ScaleAgnosticChord(
                root_wrapped_pitch=7, chord_type=ChordType.SEVENTH
            ),  # E 7
            ScaleAgnosticChord(
                root_wrapped_pitch=0, chord_type=ChordType.MINOR
            ),  # A min
            ScaleAgnosticChord(
                root_wrapped_pitch=5, chord_type=ChordType.MINOR
            ),  # D min
            ScaleAgnosticChord(
                root_wrapped_pitch=10, chord_type=ChordType.SEVENTH
            ),  # G 7
            ScaleAgnosticChord(root_wrapped_pitch=3, chord_type=ChordType.MAJOR),  # C
        ]

    def very_obviously_d_major_progression(self):
        return [
            ScaleAgnosticChord(root_wrapped_pitch=5, chord_type=ChordType.MAJOR),  # D
            ScaleAgnosticChord(root_wrapped_pitch=10, chord_type=ChordType.MAJOR),  # G
            ScaleAgnosticChord(
                root_wrapped_pitch=4, chord_type=ChordType.DIM_SEVENTH
            ),  # C# dim7
            ScaleAgnosticChord(
                root_wrapped_pitch=9, chord_type=ChordType.SEVENTH
            ),  # F# 7
            ScaleAgnosticChord(
                root_wrapped_pitch=2, chord_type=ChordType.MINOR
            ),  # B min
            ScaleAgnosticChord(
                root_wrapped_pitch=7, chord_type=ChordType.MINOR
            ),  # E min
            ScaleAgnosticChord(
                root_wrapped_pitch=0, chord_type=ChordType.SEVENTH
            ),  # A 7
            ScaleAgnosticChord(root_wrapped_pitch=5, chord_type=ChordType.MAJOR),  # D
        ]
