import soundfile as sf
import sounddevice as sd
from typing import Callable, Any
import threading

import numpy as np

from .real_time_basic_pitch import I_AudioStreamer
import resampy


class FilePlaybackIntegration(I_AudioStreamer):
    def __init__(self, audio_file_path: str):
        self.file_path = audio_file_path

    def stream_audio(
        self,
        sample_rate: int,
        num_audio_channels: int,
        callback: Callable[[np.ndarray], None],
        threading_event: threading.Event,
    ):
        MONO_CHANNELS = 1
        assert num_audio_channels == MONO_CHANNELS, "Only mono supported for playback!"
        try:
            audio_data, original_sample_rate = sf.read(self.file_path)
            resampled_audio = resampy.resample(
                x=audio_data, sr_orig=original_sample_rate, sr_new=sample_rate
            )
            if resampled_audio.ndim != 1:
                # downsample to mono if not already
                resampled_audio = np.mean(resampled_audio, axis=1)
            resampled_audio = resampled_audio[:, np.newaxis]

            current_idx = 0

            def forward_audio_chunk(
                outdata: np.ndarray, frames: int, time: Any, status: sd.CallbackFlags
            ):
                """
                Feeds data to the outputstream and to our callback simultaneously
                so that we can hear what the harmony analyzer is hearing
                """
                nonlocal current_idx
                requested_end_idx = current_idx + frames
                actual_end_idx = min(requested_end_idx, len(resampled_audio))
                if actual_end_idx < requested_end_idx:
                    available_block_size = actual_end_idx - current_idx
                    outdata[:available_block_size] = resampled_audio[
                        current_idx:actual_end_idx
                    ]
                    outdata[available_block_size:] = 0  # pad remainder with zeros
                    raise sd.CallbackStop()
                else:
                    outdata[:] = resampled_audio[current_idx:actual_end_idx]
                current_idx = actual_end_idx
                callback(outdata.copy())

            with sd.OutputStream(
                samplerate=sample_rate,
                channels=MONO_CHANNELS,
                callback=forward_audio_chunk,
                finished_callback=threading_event.set,
            ):
                threading_event.wait()

        except KeyboardInterrupt:
            print("\nStream killed by user.")

        except Exception as e:
            print(f"An error occurred: {e}")
