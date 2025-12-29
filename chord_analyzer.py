from typing import NamedTuple


from harmony_domain import (
    NoteName,
    Note,
    ChordType,
    Chord,
    HarmonyState,
    ScaleAgnosticChord,
)

"""
NOTE: "Wrapped pitches" here refers to semitones from A, zero-indexed, wrapped between 0-11 incl.
"""


class ChordAnalyzer:
    class ChordMatchingResults(NamedTuple):
        most_likely_chord: ChordType
        num_matches_for_most_likely_chord: int

    def __init__(self):
        self.KEY_INTERVALS = [3, 4, 6, 7, 9, 10]
        self.MIN_THIRD_IDX = 0
        self.MAJ_THIRD_IDX = 1
        self.TRITONE_IDX = 2
        self.P_FIFTH_IDX = 3
        self.MAJ_SIXTH_IDX = 4
        self.MIN_SEVENTH_IDX = 5

    def analyze_chord(self, pitches: list[int]):
        # midi pitch number 9 is an "A"
        pitches_wrapped = [(pitch - 9) % 12 for pitch in pitches]
        unique_pitches_wrapped = list(set(pitches_wrapped))
        if len(unique_pitches_wrapped) < 3:
            # Don't attempt to analyze anything less than a triad
            return None, unique_pitches_wrapped
        else:
            matching_results_per_root_candidate = [
                self.analyze_chord_assuming_root_pitch(
                    assumed_root_pitch=root_candidate,
                    all_pitches=unique_pitches_wrapped,
                )
                for root_candidate in unique_pitches_wrapped
            ]
            # Winner is a list to accomodate for ties
            idxs_with_highest_num_matches = []
            highest_num_matches = 0
            for root_candidate_index in range(len(unique_pitches_wrapped)):
                num_matches_for_root_candidate = matching_results_per_root_candidate[
                    root_candidate_index
                ].num_matches_for_most_likely_chord
                if num_matches_for_root_candidate == 0:
                    continue
                elif num_matches_for_root_candidate > highest_num_matches:
                    idxs_with_highest_num_matches = [root_candidate_index]
                    highest_num_matches = num_matches_for_root_candidate
                elif num_matches_for_root_candidate == highest_num_matches:
                    idxs_with_highest_num_matches.append(root_candidate_index)
            chord = None
            if idxs_with_highest_num_matches:  # check not empty
                # By default assume first index is the best, then check if there is a tie
                winning_idx = idxs_with_highest_num_matches[0]

                # Handle ties
                if len(idxs_with_highest_num_matches) > 1:
                    # Break tie by checking for lowest note
                    lowest_wrapped_pitch = (min(pitches) - 9) % 12
                    for candidate_idx in idxs_with_highest_num_matches:
                        root_at_candidate_idx = unique_pitches_wrapped[candidate_idx]
                        if lowest_wrapped_pitch == root_at_candidate_idx:
                            winning_idx = candidate_idx

                chord = ScaleAgnosticChord(
                    root_wrapped_pitch=unique_pitches_wrapped[winning_idx],
                    chord_type=matching_results_per_root_candidate[
                        winning_idx
                    ].most_likely_chord,
                )
            return chord, unique_pitches_wrapped

    def analyze_chord_assuming_root_pitch(
        self, assumed_root_pitch: int, all_pitches: list[int]
    ) -> ChordMatchingResults:
        intervals_up_from_assumed_root = [
            (pitch - assumed_root_pitch) % 12 for pitch in all_pitches
        ]
        # Indices of the following line up the the indices declared in ctor
        # (What I did here was probably a completely unnecessary optimization)
        key_interval_matches = [
            1 if (key_int in intervals_up_from_assumed_root) else 0
            for key_int in self.KEY_INTERVALS
        ]
        number_matches_for_major_chord = (
            key_interval_matches[self.MAJ_THIRD_IDX]
            + key_interval_matches[self.P_FIFTH_IDX]
            + key_interval_matches[self.MIN_SEVENTH_IDX]
        )
        number_matches_for_minor_chord = (
            key_interval_matches[self.MIN_THIRD_IDX]
            + key_interval_matches[self.P_FIFTH_IDX]
            + key_interval_matches[self.MIN_SEVENTH_IDX]
        )
        number_matches_for_diminished_chord = (
            key_interval_matches[self.MIN_THIRD_IDX]
            + key_interval_matches[self.TRITONE_IDX]
            + key_interval_matches[self.MAJ_SIXTH_IDX]
        )
        results = None
        if (
            number_matches_for_major_chord > number_matches_for_minor_chord
            and number_matches_for_major_chord > number_matches_for_diminished_chord
        ):
            seventh_found = key_interval_matches[self.MIN_SEVENTH_IDX] > 0
            results = self.ChordMatchingResults(
                most_likely_chord=(
                    ChordType.SEVENTH if seventh_found else ChordType.MAJOR
                ),
                num_matches_for_most_likely_chord=number_matches_for_major_chord,
            )
        elif (
            number_matches_for_minor_chord > number_matches_for_major_chord
            and number_matches_for_minor_chord > number_matches_for_diminished_chord
        ):
            seventh_found = key_interval_matches[self.MIN_SEVENTH_IDX] > 0
            results = self.ChordMatchingResults(
                most_likely_chord=(
                    ChordType.MIN_SEVENTH if seventh_found else ChordType.MINOR
                ),
                num_matches_for_most_likely_chord=number_matches_for_minor_chord,
            )
        else:
            seventh_found = key_interval_matches[self.MAJ_SIXTH_IDX] > 0
            results = self.ChordMatchingResults(
                most_likely_chord=(
                    ChordType.DIM_SEVENTH if seventh_found else ChordType.DIMINISHED
                ),
                num_matches_for_most_likely_chord=number_matches_for_diminished_chord,
            )
        # TODO: do we need to break ties here?
        return results
