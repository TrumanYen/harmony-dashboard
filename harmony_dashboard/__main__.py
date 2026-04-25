from .app import App
from .physical_mic_integration import PhysicalMicIntegration
from .real_time_basic_pitch import PitchDetectingAudioStreamer
from .harmony import HarmonyModule
from .ui import TkinterAdapter


if __name__ == "__main__":
    physical_mic_streamer = PhysicalMicIntegration()
    pitch_detecting_audio_streamer = PitchDetectingAudioStreamer(
        audio_streamer=physical_mic_streamer
    )
    harmony_analyzer = HarmonyModule()
    presenter = TkinterAdapter()

    app = App(
        pitch_streamer=pitch_detecting_audio_streamer,
        harmony_analyzer=harmony_analyzer,
        presenter=presenter,
    )

    app.run()
