from chord_predictor import I_HarmonyAnalyzer


class HarmonyAnalyzer(I_HarmonyAnalyzer):
    def __init__(self):
        pass

    def new_pitches_detected(self, pitches: list[int]):
        print("Analyzing pitches: " + str(pitches))
