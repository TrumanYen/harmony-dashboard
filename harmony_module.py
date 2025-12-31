from app import I_HarmonyAnalyzer, I_HarmonyStateListener
from harmony_domain import NoteName, Note, ChordType, Chord, HarmonyState
from chord_analyzer import ChordAnalyzer
from tonal_center_detector import ScaleAnalyzer

"""
NOTE: "Wrapped pitches" here refers to semitones from A, zero-indexed, wrapped between 0-11 incl.
"""


class DummyListener(I_HarmonyStateListener):
    def update_harmony_state(self, state: HarmonyState):
        pass


class HarmonyModule(I_HarmonyAnalyzer):
    def __init__(self):
        self.listener = DummyListener()
        self.chord_analyzer = ChordAnalyzer()
        self.scale_analyzer = ScaleAnalyzer()

    def register_listener(self, listener: I_HarmonyStateListener):
        self.listener = listener

    def new_pitches_detected(self, pitches: list[int]):
        if not pitches:
            return
        scale_agnostic_chord, unique_pitches_wrapped = (
            self.chord_analyzer.analyze_chord(pitches)
        )
        chord_in_current_scale = None
        if scale_agnostic_chord:
            chord_in_current_scale = Chord(
                root=self.scale_analyzer.map_wrapped_pitch_to_note(
                    scale_agnostic_chord.root_wrapped_pitch
                ),
                chord_type=scale_agnostic_chord.chord_type,
            )
        notes_detected_in_current_scale = [
            self.scale_analyzer.map_wrapped_pitch_to_note(wrapped_pitch)
            for wrapped_pitch in unique_pitches_wrapped
        ]
        self.listener.update_harmony_state(
            HarmonyState(
                current_major_scale=None,
                current_chord=chord_in_current_scale,
                notes_detected=notes_detected_in_current_scale,
            )
        )
