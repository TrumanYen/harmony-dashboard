from .app import App
from .real_time_basic_pitch import PitchDetectingAudioStreamer
from .harmony_module import HarmonyModule
from .ui import TkinterAdapter


if __name__ == "__main__":
    pitch_detecting_audio_streamer = PitchDetectingAudioStreamer()
    harmony_analyzer = HarmonyModule()
    presenter = TkinterAdapter()

    app = App(
        pitch_streamer=pitch_detecting_audio_streamer,
        harmony_analyzer=harmony_analyzer,
        presenter=presenter,
    )

    app.run()
