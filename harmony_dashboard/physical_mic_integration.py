import sounddevice as sd
from typing import Callable, Any
import threading
import sys

import numpy as np

from .real_time_basic_pitch import I_AudioStreamer


class PhysicalMicIntegration(I_AudioStreamer):
    def __init__(self):
        pass

    def stream_audio(
        self,
        sample_rate: int,
        num_audio_channels: int,
        callback: Callable[[np.ndarray], None],
        threading_event: threading.Event,
    ):
        def forward_audio_chunk(
            indata: np.ndarray, frames: int, time: Any, status: sd.CallbackFlags
        ):
            if status:
                print(f"Status flags: {status}", file=sys.stderr)
            callback(indata.copy())

        try:
            with sd.InputStream(
                samplerate=sample_rate,
                channels=num_audio_channels,
                callback=forward_audio_chunk,
            ):
                threading_event.wait()

        except KeyboardInterrupt:
            print("\nStream killed by user.")

        except Exception as e:
            print(f"An error occurred: {e}")
