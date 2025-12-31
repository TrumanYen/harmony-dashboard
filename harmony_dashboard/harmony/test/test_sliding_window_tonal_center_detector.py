import pytest
from unittest.mock import Mock
import random


from ...harmony_domain import ScaleAgnosticChord, ChordType
from ..tonal_center_detector import (
    I_ConvolutionalTonalCenterDetector,
    SlidingWindowTonalCenterDetector,
)


class TestSlidingWindowTonalCenterDetector:
    EXPECTED_SLIDING_WINDOW_SIZE = 10

    @pytest.fixture(autouse=True)
    def before_each_test(self):
        self.convolutional_tonal_center_detector = Mock(
            spec=I_ConvolutionalTonalCenterDetector
        )
        self.patient = SlidingWindowTonalCenterDetector(
            self.convolutional_tonal_center_detector
        )

    def test_will_fill_sliding_window_with_unique_chords(self):
        for i in range(self.EXPECTED_SLIDING_WINDOW_SIZE):
            chord = ScaleAgnosticChord(i % 12, ChordType.MAJOR)
            self.patient.recalculate_tonal_center_given_new_chord(chord)
        assert (
            self.convolutional_tonal_center_detector.insert_chord.call_count
            == self.EXPECTED_SLIDING_WINDOW_SIZE
        )

    def test_will_dequeue_oldest_chord_after_sliding_window_filled(self):
        expected_oldest_chord = ScaleAgnosticChord(0, ChordType.DIMINISHED)
        self.patient.recalculate_tonal_center_given_new_chord(expected_oldest_chord)
        for i in range(self.EXPECTED_SLIDING_WINDOW_SIZE):
            chord = ScaleAgnosticChord(i % 12, ChordType.MAJOR)
            self.patient.recalculate_tonal_center_given_new_chord(chord)

        self.convolutional_tonal_center_detector.remove_chord.assert_called_once_with(
            expected_oldest_chord
        )

        assert (
            self.convolutional_tonal_center_detector.insert_chord.call_count
            == self.EXPECTED_SLIDING_WINDOW_SIZE + 1
        )

    def test_will_not_enqueue_unchanged_chord(self):
        arbitrary_chord = ScaleAgnosticChord(0, ChordType.MAJOR)
        self.patient.recalculate_tonal_center_given_new_chord(arbitrary_chord)

        self.patient.recalculate_tonal_center_given_new_chord(arbitrary_chord)

        self.convolutional_tonal_center_detector.insert_chord.assert_called_once()

    def test_will_recalculate_convolutional_tonal_center_detector_every_new_chord(self):
        arbitrary_chord = ScaleAgnosticChord(0, ChordType.MAJOR)

        self.patient.recalculate_tonal_center_given_new_chord(arbitrary_chord)

        self.convolutional_tonal_center_detector.predict_tonal_center.assert_called_once()

    def test_will_provide_correct_current_tonal_center(self):
        expected_tonal_center = random.randint(0, 11)
        self.convolutional_tonal_center_detector.predict_tonal_center.return_value = (
            expected_tonal_center
        )
        arbitrary_chord = ScaleAgnosticChord(0, ChordType.MAJOR)
        self.patient.recalculate_tonal_center_given_new_chord(arbitrary_chord)

        assert self.patient.current_tonal_center == expected_tonal_center
