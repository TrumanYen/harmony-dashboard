from chord_predictor import ChordPredictor, I_HarmonyPresenter
from harmony_domain import HarmonyState
from real_time_basic_pitch import PitchDetectingAudioStreamer
from harmony_analyzer import HarmonyAnalyzer


class DummyHarmonyPresenter(I_HarmonyPresenter):
    def update_harmony_state(self, state: HarmonyState):
        pass

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
