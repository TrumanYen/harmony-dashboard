from argparse import ArgumentParser

from .app import App
from .physical_mic_integration import PhysicalMicIntegration
from .file_playback_integration import FilePlaybackIntegration
from .real_time_basic_pitch import PitchDetectingAudioStreamer
from .harmony import HarmonyModule
from .ui import TkinterAdapter


def main(playback_input_path: str | None):
    audio_streamer = (
        PhysicalMicIntegration()
        if playback_input_path is None
        else FilePlaybackIntegration(args.playback_input)
    )
    pitch_detecting_audio_streamer = PitchDetectingAudioStreamer(
        audio_streamer=audio_streamer
    )
    harmony_analyzer = HarmonyModule()
    presenter = TkinterAdapter()

    app = App(
        pitch_streamer=pitch_detecting_audio_streamer,
        harmony_analyzer=harmony_analyzer,
        presenter=presenter,
    )

    app.run()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--playback_input",
        help="If an audio file path is provided with this argument, the app will play back that file rather than connecting to a mic",
        required=False,
        default=None,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(playback_input_path=args.playback_input)
