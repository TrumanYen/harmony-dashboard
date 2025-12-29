from harmony_domain import NoteName, Note, ChordType, Chord, HarmonyState


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
