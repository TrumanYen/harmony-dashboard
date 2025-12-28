import queue
from abc import ABC, abstractmethod
import threading
import time
import sys
from typing import Any

from basic_pitch.inference import predict, Model
from basic_pitch import ICASSP_2022_MODEL_PATH
import numpy as np
import soundfile as sf
import sounddevice as sd


class I_PitchStreamListener(ABC):
    @abstractmethod
    def new_pitches_detected(self, pitches: list[int]):
        pass


class PitchDetectingAudioStreamer:
    def __init__(self, listener: I_PitchStreamListener):
        self.listener = listener
        self.audio_block_queue = queue.Queue()
        self.thread_event = threading.Event()
        self.pitch_detection_thread = threading.Thread(
            target=self._periodically_detect_pitches
        )
        self.audio_streaming_thread = threading.Thread(target=self._stream_audio)

        self.pitch_detection_sample_period_sec = 0.2
        self.sample_rate = 22050  # Sample rate used by basic pitch
        self.audio_channels = 1  # basic pitch samples down to mono anyways
        self.audio_sample_subtype = "PCM_16"
        self.audio_sample_file_path = "./temp.wav"
        self.basic_pitch_model = Model(ICASSP_2022_MODEL_PATH)
        # Min and max frequencies to allow basic pitch to look for:
        self.min_freq_hz = 27.5
        self.max_freq_hz = 2093.0

    def start_streaming(self):
        self.pitch_detection_thread.start()
        self.audio_streaming_thread.start()

    def stop_streaming(self):
        self.thread_event.set()
        self.audio_streaming_thread.join()
        self.pitch_detection_thread.join()

    def _periodically_detect_pitches(self):
        while not self.thread_event.is_set():
            audio_blocks = []
            while not self.audio_block_queue.empty():
                audio_blocks.append(self.audio_block_queue.get())
            if audio_blocks:
                combined_sample = np.concatenate(audio_blocks, axis=0)
                # Write the block of of sound to disk
                with sf.SoundFile(
                    self.audio_sample_file_path,
                    mode="w",
                    samplerate=self.sample_rate,
                    channels=self.audio_channels,
                    subtype=self.audio_sample_subtype,
                ) as file:
                    file.write(combined_sample)
                # Make basic pitch read it back out of disk (sigh)
                model_output, midi_data, note_events = predict(
                    audio_path=self.audio_sample_file_path,
                    model_or_model_path=self.basic_pitch_model,
                    minimum_frequency=self.min_freq_hz,
                    maximum_frequency=self.max_freq_hz,
                )
                # Print out detected notes
                if len(midi_data.instruments) > 0:
                    instrument = midi_data.instruments[0]
                    pitches = [note.pitch for note in instrument.notes]
                    self.listener.new_pitches_detected(pitches)
            time.sleep(self.pitch_detection_sample_period_sec)

    def _stream_audio(self):
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.audio_channels,
                callback=self._enqueue_audio_block,
            ):
                # The 'with' statement manages the stream; it runs in the background.
                # The main thread can do other things or simply wait.
                self.thread_event.wait()
        except KeyboardInterrupt:
            print("\nStream killed by user.")

        except Exception as e:
            print(f"An error occurred: {e}")

    def _enqueue_audio_block(
        self, indata: np.ndarray, frames: int, time: Any, status: sd.CallbackFlags
    ):
        if status:
            print(f"Status flags: {status}", file=sys.stderr)
        self.audio_block_queue.put(indata.copy())
