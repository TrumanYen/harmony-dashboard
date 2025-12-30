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


class ConvolutionalScaleDetector:
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
        return np.argmax(prediction_vector)
