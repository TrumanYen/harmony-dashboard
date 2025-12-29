from chord_predictor import ChordPredictor, I_HarmonyPresenter
from harmony_domain import HarmonyState
from real_time_basic_pitch import PitchDetectingAudioStreamer
from harmony_analyzer import HarmonyAnalyzer


class DummyHarmonyPresenter(I_HarmonyPresenter):
    def update_harmony_state(self, state: HarmonyState):
        current_chord = state.current_chord
        if current_chord:
            note_name = current_chord.root.note_name.name
            note_accidental = "#" if current_chord.root.accidentals == 1 else ""
            print(
                f"Current chord: {note_name}{note_accidental} {current_chord.chord_type.name}"
            )

    def run_ui_until_stopped_by_user(self):
        pass


if __name__ == "__main__":
    pitch_detecting_audio_streamer = PitchDetectingAudioStreamer()
    harmony_analyzer = HarmonyAnalyzer()
    presenter = DummyHarmonyPresenter()  # TODO: use a real presenter

    chord_predictor = ChordPredictor(
        pitch_streamer=pitch_detecting_audio_streamer,
        harmony_analyzer=harmony_analyzer,
        presenter=presenter,
    )

    chord_predictor.run()
