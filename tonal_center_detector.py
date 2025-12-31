from abc import ABC, abstractmethod
from collections import deque

import numpy as np

from harmony_domain import (
    NoteName,
    Note,
    ChordType,
    Chord,
    HarmonyState,
    ScaleAgnosticChord,
)


class ScaleAnalyzer:
    def __init__(self):
        self.DEFAULT_WRAPPED_PITCH_TO_NOTE_MAPPING = [
            Note(NoteName.A, 0),
            Note(NoteName.A, 1),
            Note(NoteName.B, 0),
            Note(NoteName.C, 0),
            Note(NoteName.C, 1),
            Note(NoteName.D, 0),
            Note(NoteName.D, 1),
            Note(NoteName.E, 0),
            Note(NoteName.F, 0),
            Note(NoteName.F, 1),
            Note(NoteName.G, 0),
            Note(NoteName.G, 1),
        ]
        # TODO: actually detect scale and apply correct accidentals

    def map_wrapped_pitch_to_note(self, wrapped_pitch: int):
        return self.DEFAULT_WRAPPED_PITCH_TO_NOTE_MAPPING[wrapped_pitch]


class I_ConvolutionalTonalCenterDetector(ABC):
    @abstractmethod
    def insert_chord(self, chord: ScaleAgnosticChord):
        pass

    @abstractmethod
    def remove_chord(self, chord: ScaleAgnosticChord):
        pass

    @abstractmethod
    def predict_tonal_center(self) -> int:
        pass


class SlidingWindowTonalCenterDetector:
    """
    Uses the ConvolutionalTonalCenterDetector under the hood, but manages a sliding window
    of chords to feed into the ConvolutionalTonalCenterDetector
    """

    def __init__(
        self, convolutional_scale_detector: I_ConvolutionalTonalCenterDetector
    ):
        self.SLIDING_WINDOW_SIZE = 10
        self.convolutional_scale_detector = convolutional_scale_detector
        self.fifo_chord_window = deque()
        self.current_tonal_center = None

    def recalculate_tonal_center_given_new_chord(self, chord: ScaleAgnosticChord):
        if self.fifo_chord_window and chord == self.fifo_chord_window[-1]:
            # chord was not changed since last update
            return
        self.fifo_chord_window.append(chord)
        self.convolutional_scale_detector.insert_chord(chord)
        if len(self.fifo_chord_window) > self.SLIDING_WINDOW_SIZE:
            oldest_chord = self.fifo_chord_window.popleft()
            self.convolutional_scale_detector.remove_chord(oldest_chord)

        self.current_tonal_center = (
            self.convolutional_scale_detector.predict_tonal_center()
        )


class ConvolutionalTonalCenterDetector(I_ConvolutionalTonalCenterDetector):
    """
    jist of the algorithm:
    - represent recently detected chords in a 2d array where rows are the chord type
      and columns are the root note (wrapped between A and G#)
    - each tonal center can be represented as a kernel (reward certain chords like
      tonic, dominant, submediant, while punishing other chords that don't fit)
    - The kernels for each tonal center are identical but shifted (and wrapped)
      along the x axis, so they are translation invariant.
    - Use convolution to find the most likely tonal center like you would use
      convolution to detect the location of a specific shape in an image
    """

    def __init__(self):
        self.chord_type_to_row_num_map = {
            ChordType.MAJOR: 0,
            ChordType.SEVENTH: 0,
            ChordType.MINOR: 1,
            ChordType.MIN_SEVENTH: 1,
            ChordType.DIMINISHED: 2,
            ChordType.DIM_SEVENTH: 2,
        }
        # Rows indices represent chord type, column indices represent chord roots in incrementing by
        # semitone starting at A=0.  These values are populated by my personal experience as a classical
        # musicion; basically this is machine learning in the sense that I told the machine what to think
        # and it learned to obey me.
        KERNEL_TEMPLATE_A_MAJOR = np.array(
            [
                [1, -1, 0, -1, 1, 1, -1, 1, -1, 0, -1, 0],  # maj
                [-1, -1, 1, -1, 1, 0, -1, 0, -1, 1, -1, 0],  # min
                [-1, -1, 1, -1, -1, 1, -1, -1, 1, -1, -1, 1],  # dim
            ]
        )
        # Circular convolution, each time shifting the kernel to the right.  Each shifted version
        # of the kernel gets stacked, such that we now have 12x kernels, each representing one
        # tonal center.
        self.kernels_3d = np.stack(
            [np.roll(KERNEL_TEMPLATE_A_MAJOR, shift=i, axis=1) for i in range(12)],
            axis=0,
        )
        # This is the array that will get modified as chords are inserted and removed:
        self.input_chord_data = np.zeros(shape=(3, 12), dtype=np.int8)

    def insert_chord(self, chord: ScaleAgnosticChord):
        row_num = self.chord_type_to_row_num_map[chord.chord_type]
        self.input_chord_data[row_num][chord.root_wrapped_pitch] += 1

    def remove_chord(self, chord: ScaleAgnosticChord):
        row_num = self.chord_type_to_row_num_map[chord.chord_type]
        current_value_at_index = self.input_chord_data[row_num][
            chord.root_wrapped_pitch
        ]
        self.input_chord_data[row_num][chord.root_wrapped_pitch] = max(
            0, current_value_at_index - 1
        )

    def predict_tonal_center(self):
        prediction_vector = np.sum(self.kernels_3d * self.input_chord_data, axis=(1, 2))
        if not np.any(prediction_vector):
            return None
        return np.argmax(prediction_vector)
