from chord_predictor import I_HarmonyAnalyzer, I_HarmonyStateListener
from harmony_domain import NoteName, Note, ChordType, Chord, HarmonyState


class HarmonyAnalyzer(I_HarmonyAnalyzer):
    def __init__(self):
        pass

    def register_listener(self, listener: I_HarmonyStateListener):
        pass

    def new_pitches_detected(self, pitches: list[int]):
        print("Analyzing pitches: " + str(pitches))
