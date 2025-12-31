from ..app import I_HarmonyAnalyzer, I_HarmonyStateListener
from ..harmony_domain import HarmonyState
from .chord_analyzer import ChordAnalyzer
from .tonal_center_detector import (
    SlidingWindowTonalCenterDetector,
    ConvolutionalTonalCenterDetector,
)
from .enharmonic_resolver import EnharmonicResolver

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
        self.convolutional_tonal_center_detector = ConvolutionalTonalCenterDetector()
        self.sliding_window_tonal_center_detector = SlidingWindowTonalCenterDetector(
            self.convolutional_tonal_center_detector
        )
        self.enharmonic_resolver = EnharmonicResolver()

    def register_listener(self, listener: I_HarmonyStateListener):
        self.listener = listener

    def new_pitches_detected(self, pitches: list[int]):
        if not pitches:
            return
        scale_agnostic_chord, unique_pitches_wrapped = (
            self.chord_analyzer.analyze_chord(pitches)
        )
        tonal_center_wrapped_pitch = None
        if scale_agnostic_chord:
            self.sliding_window_tonal_center_detector.recalculate_tonal_center_given_new_chord(
                scale_agnostic_chord
            )
        tonal_center_wrapped_pitch = (
            self.sliding_window_tonal_center_detector.current_tonal_center
        )

        self.listener.update_harmony_state(
            self.enharmonic_resolver.convert_from_wrapped_pitches_to_notes(
                new_tonal_center_wrapped_pitch=tonal_center_wrapped_pitch,
                new_chord=scale_agnostic_chord,
                detected_notes_wrapped_pitches=unique_pitches_wrapped,
            )
        )
