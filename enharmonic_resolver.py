from math import ceil, floor

from harmony_domain import (
    Note,
    NoteName,
    ScaleAgnosticChord,
    HarmonyState,
    Chord,
    ChordType,
)

"""
The concept of a circle_index here is the index of some note
in the circle of fifths, starting at C=0.  For example:

Db = -5
Ab = -4
Eb = -3
Bb = -2
F = -1
C = 0
G = 1
D = 2
A = 3
E = 4
B = 5
F# = 6
C# = 7

Note that '-5' and '7' are enharmonic equivalents but are
conceptually different in terms of their locations on the circle.

tl;dr we are using the circle of fifths in ways that were probably
not originally intended
"""


class EnharmonicResolver:
    def __init__(self):
        self.circle_index_calculator = CircleIndexCalculator()

        self.current_tonal_center_wrapped_pitch = None
        self.current_tonal_center_circle_index = None
        self.current_tonal_center_note = None

        self.current_scale_agnostic_chord = None
        self.current_chord_root_circle_index = None
        self.current_chord = None

    def convert_from_wrapped_pitches_to_notes(
        self,
        new_tonal_center_wrapped_pitch: int | None,
        new_chord: ScaleAgnosticChord | None,
        detected_notes_wrapped_pitches: list[int],
    ) -> HarmonyState:
        no_cached_tonal_center = (
            self.current_tonal_center_wrapped_pitch is None
            or self.current_tonal_center_circle_index is None
            or self.current_tonal_center_note is None
        )
        new_tonal_center_discovered = (
            new_tonal_center_wrapped_pitch is not None
            and new_tonal_center_wrapped_pitch
            != self.current_tonal_center_wrapped_pitch
        )
        if no_cached_tonal_center or new_tonal_center_discovered:
            self._resolve_tonal_center(new_tonal_center_wrapped_pitch)

        new_chord_discovered = new_chord is not None and new_chord != self.current_chord
        if new_chord_discovered:
            self._resolve_chord_root(new_chord)

        return HarmonyState(
            current_major_scale=self.current_tonal_center_note,
            current_chord=self.current_chord,
            notes_detected=self._resolve_detected_notes(detected_notes_wrapped_pitches),
        )

    def _resolve_tonal_center(self, tonal_center_wrapped_pitch: int | None):
        if tonal_center_wrapped_pitch is not None:
            self.current_tonal_center_wrapped_pitch = tonal_center_wrapped_pitch
            # Get circle index of scale closest to C so there's as few sharps and flats as possible
            self.current_tonal_center_circle_index = self.circle_index_calculator.circle_index_for_enharmonic_equivalent_closest_to_tonal_center(
                wrapped_pitch=tonal_center_wrapped_pitch,
                tonal_center_circle_index=0,
            )
            self.current_tonal_center_note = (
                self.circle_index_calculator.convert_circle_index_to_note(
                    self.current_tonal_center_circle_index
                )
            )
        else:
            # assume c major if not provided
            self.current_tonal_center_circle_index = 0

    def _resolve_chord_root(self, new_chord: ScaleAgnosticChord):
        candidate_chord_root_circle_index = self.circle_index_calculator.circle_index_for_enharmonic_equivalent_within_scale_if_exists(
            wrapped_pitch=new_chord.root_wrapped_pitch,
            scale_tonal_center_circle_index=self.current_tonal_center_circle_index,
        )
        if candidate_chord_root_circle_index is not None:
            self.current_chord_root_circle_index = candidate_chord_root_circle_index
        else:
            # Note that we might not have gotten a chord root circle index if it doesn't
            # belong in the current scale.  In this case, use whatever is closest to the
            # last chord we got.  If we don't have a previous chord we can use the scale
            tonal_center = (
                self.current_chord_root_circle_index
                if self.current_chord_root_circle_index is not None
                else self.current_tonal_center_circle_index
            )
            self.current_chord_root_circle_index = self.circle_index_calculator.circle_index_for_enharmonic_equivalent_closest_to_tonal_center(
                wrapped_pitch=new_chord.root_wrapped_pitch,
                tonal_center_circle_index=tonal_center,
            )
        self.current_chord = Chord(
            root=self.circle_index_calculator.convert_circle_index_to_note(
                self.current_chord_root_circle_index
            ),
            chord_type=new_chord.chord_type,
        )

    def _resolve_detected_notes(
        self, detected_notes_wrapped_pitches: list[int]
    ) -> list[Note]:
        detected_notes = []
        for pitch in detected_notes_wrapped_pitches:
            circle_index = self.circle_index_calculator.circle_index_for_enharmonic_equivalent_within_scale_if_exists(
                wrapped_pitch=pitch,
                scale_tonal_center_circle_index=self.current_tonal_center_circle_index,
            )
            if circle_index is None:
                # If note is not strictly part of scale, base it off current chord.  If that's not available base it off
                # E such that all black keys are sharps
                current_chord_circle_index = (
                    self.current_chord_root_circle_index
                    if self.current_chord_root_circle_index is not None
                    else 4
                )
                circle_index = self.circle_index_calculator.circle_index_for_enharmonic_equivalent_closest_to_tonal_center(
                    wrapped_pitch=pitch,
                    tonal_center_circle_index=current_chord_circle_index,
                )
            detected_notes.append(
                self.circle_index_calculator.convert_circle_index_to_note(circle_index)
            )
        return detected_notes


class CircleIndexCalculator:
    def __init__(self):
        self.wrapped_circle_index_to_note_name_map = {
            0: NoteName.C,
            1: NoteName.G,
            2: NoteName.D,
            3: NoteName.A,
            4: NoteName.E,
            5: NoteName.B,
            6: NoteName.F,
        }

    def circle_index_for_enharmonic_equivalent_closest_to_tonal_center(
        self, wrapped_pitch: int, tonal_center_circle_index: int
    ) -> int:
        """
        Find the enharmonic equivalent for wrapped_pitch such that it is
        as close to tonal_center_circle_index as possible on the circle of fifths.
        Return as a circle index.  For example, if you're working in A major,
        a G# chord would make more sense than an Ab chord.
        """
        return (
            self._smallest_circle_index_delta_from_tonal_center(
                wrapped_pitch=wrapped_pitch,
                tonal_center_circle_index=tonal_center_circle_index,
            )
            + tonal_center_circle_index
        )

    def circle_index_for_enharmonic_equivalent_within_scale_if_exists(
        self, wrapped_pitch: int, scale_tonal_center_circle_index: int
    ) -> int | None:
        """
        Effectively applies a key signature or returns none if the note is
        note in the selected scale.
        """

        smallest_circle_index_delta = (
            self._smallest_circle_index_delta_from_tonal_center(
                wrapped_pitch=wrapped_pitch,
                tonal_center_circle_index=scale_tonal_center_circle_index,
            )
        )
        # I discovered that for a given tonal center the notes of the major scale
        # are within the following range.  This basically saves us from having to
        # hard-code key signatures.  The very silly benefit of this is that we can
        # technically keep spiralling up or down the circle of fifths until we
        # have so many sharps or flats we integer overflow
        if smallest_circle_index_delta >= -1 and smallest_circle_index_delta <= 5:
            return smallest_circle_index_delta + scale_tonal_center_circle_index
        else:
            return None

    def convert_circle_index_to_note(self, circle_index: int) -> Note:
        """
        The moment we've all been waiting for
        """
        note_name = self.wrapped_circle_index_to_note_name_map[circle_index % 7]
        accidentals = 0
        if circle_index > 5:  # F# or greater
            accidentals = ceil((circle_index - 5) / 7)
        elif circle_index < -1:  # Bb or less
            accidentals = floor((circle_index + 1) / 7)

        return Note(note_name, accidentals)

    def _smallest_circle_index_delta_from_tonal_center(
        self, wrapped_pitch: int, tonal_center_circle_index: int
    ):
        # First translate 3 indices down because circle indices are based off C=0,
        # while pitches are based off A=0.  For example, 'A' would have a circle index
        # of 3 but should have a pitch of 0.
        tonal_center_as_pitch = (tonal_center_circle_index - 3) * 7
        # Get delta in pitches
        pitches_above_tonal_center = wrapped_pitch - tonal_center_as_pitch
        # Calculate smallest possible delta in circle indices
        smallest_positive_delta = (7 * pitches_above_tonal_center) % 12
        smallest_possible_delta = (
            smallest_positive_delta
            if smallest_positive_delta <= 6
            else smallest_positive_delta - 12
        )
        return smallest_possible_delta
