from argparse import ArgumentParser
from datetime import datetime
import os
from pathlib import Path

from .app import App
from .physical_mic_integration import PhysicalMicIntegration
from .file_playback_integration import FilePlaybackIntegration
from .real_time_basic_pitch import PitchDetectingAudioStreamer
from .harmony import HarmonyModule
from .ui import TkinterAdapter
from .harmony_state_logging import LoggingHarmonyPresenterDecorator


def create_log_path(log_dir: str) -> str:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file_name = f"{datetime.now():%Y-%m-%d-%H-%M-%S}.csv"
    log_path = os.path.join(log_dir, log_file_name)
    print(f"Writing logs to {log_path}")
    return log_path


def main(playback_input_path: str | None, log_dir: str | None):
    audio_streamer = (
        PhysicalMicIntegration()
        if playback_input_path is None
        else FilePlaybackIntegration(args.playback_input)
    )
    pitch_detecting_audio_streamer = PitchDetectingAudioStreamer(
        audio_streamer=audio_streamer
    )
    harmony_analyzer = HarmonyModule()
    gui_presenter = TkinterAdapter()
    presenter = (
        gui_presenter
        if log_dir is None
        else LoggingHarmonyPresenterDecorator(
            underlying_presenter=gui_presenter, log_path=create_log_path(log_dir)
        )
    )

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
    parser.add_argument(
        "-l",
        "--log_dir",
        help="If a directory path is provided at this argument, the app write its outputs to a csv file in that directory",
        required=False,
        default=None,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(playback_input_path=args.playback_input, log_dir=args.log_dir)
