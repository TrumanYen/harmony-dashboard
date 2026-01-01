from collections import deque

import numpy as np

from ..harmony_domain import (
    ChordType,
    ScaleAgnosticChord,
)

"""
NOTE: "Wrapped pitches" here refers to semitones from A, zero-indexed, wrapped between 0-11 incl.
"""


class ChordAnalyzer:

    def __init__(self):
        self.chord_types_by_row_index = [
            ChordType.MAJOR,
            ChordType.SEVENTH,
            ChordType.MAJ_SEVENTH,
            ChordType.MINOR,
            ChordType.MIN_SEVENTH,
            ChordType.DIMINISHED,
            ChordType.DIM_SEVENTH,
        ]
        # Root note gets 3 points, fifth gets 2 points, third and sevenths get 1 each
        KERNEL_TEMPLATE = np.array(
            [
                [3, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0],  # Major
                [3, 0, 0, 0, 1, 0, 0, 2, 0, 0, 1, 0],  # Seventh
                [3, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 1],  # Maj Seventh
                [3, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0],  # Minor
                [3, 0, 0, 1, 0, 0, 0, 2, 0, 0, 1, 0],  # Min Seventh
                [3, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0],  # Diminished
                [3, 0, 0, 1, 0, 0, 2, 0, 0, 1, 0, 0],  # Diminished Seventh
            ]
        )
        # Circular convolution along the pitch axis (columns)
        self.kernels_3d = np.stack(
            [np.roll(KERNEL_TEMPLATE, shift=i, axis=1) for i in range(12)]
        )
        self.historical_scores_queue = deque()
        self.historical_scores_sliding_window_size = 10

    def analyze_chord(self, pitches: list[int]):
        # midi pitch number 9 is an "A"
        pitches_wrapped = [(pitch - 9) % 12 for pitch in pitches]
        unique_pitches_wrapped = list(set(pitches_wrapped))
        if len(unique_pitches_wrapped) < 2:
            return None, unique_pitches_wrapped
        octave_array = np.zeros(shape=(1, 12), dtype=np.int8)
        for pitch in unique_pitches_wrapped:
            octave_array[0][pitch] = 1
        octave_array_repeated = np.tile(
            octave_array, (self.kernels_3d.shape[1], 1)
        )  # Duplicate this row for however many chords we have
        # Perform convolution. Results in 2d array such that axis 0 is the root pitch and axis 1 is the chord type
        prediction_array = np.sum(self.kernels_3d * octave_array_repeated, axis=2)
        flattened_index = np.argmax(prediction_array)
        highest_value = prediction_array.flat[flattened_index]
        score_is_better_than_recent_scores = (
            not self.historical_scores_queue
            or highest_value >= max(self.historical_scores_queue)
        )
        use_answer = highest_value > 5 or score_is_better_than_recent_scores
        self._store_score_in_queue(highest_value)

        winning_coordinate_pairs = np.argwhere(prediction_array == highest_value)
        number_winners = len(winning_coordinate_pairs)
        if (not use_answer) or number_winners == 0:
            # Second case shouldn't happen but just in case
            return None, unique_pitches_wrapped
        # By default choose the first one
        root_pitch = winning_coordinate_pairs[0][0]
        chord_index = winning_coordinate_pairs[0][1]
        if number_winners > 1:
            # Tie detected. Break tie by considering lowest note.
            lowest_wrapped_pitch = (min(pitches) - 9) % 12
            for coordinate_pair in winning_coordinate_pairs:
                # Check if lowest note corresponds to root note in candidate
                root_note_for_candidate = coordinate_pair[0]
                if root_note_for_candidate == lowest_wrapped_pitch:
                    root_pitch = root_note_for_candidate
                    chord_index = coordinate_pair[1]
                    break
        chord = ScaleAgnosticChord(
            root_wrapped_pitch=root_pitch,
            chord_type=self.chord_types_by_row_index[chord_index],
        )
        return chord, unique_pitches_wrapped

    def _store_score_in_queue(self, score: int):
        self.historical_scores_queue.append(score)
        if (
            len(self.historical_scores_queue)
            > self.historical_scores_sliding_window_size
        ):
            self.historical_scores_queue.popleft()
