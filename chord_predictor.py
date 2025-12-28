from abc import ABC, abstractmethod


# Interfaces
class I_PitchStreamListener(ABC):
    """
    Callback to be passed into an I_PitchStreamer.
    """

    @abstractmethod
    def new_pitches_detected(self, pitches: list[int]):
        pass


class I_PitchStreamer(ABC):
    """
    Expected to stream audio, sampling that stream at a high frequency to
    detect individual pitches.  Should notify the listener in real time
    with those pitches as they are detected.
    """

    @abstractmethod
    def start_streaming(self, stream_listener: I_PitchStreamListener):
        pass

    @abstractmethod
    def stop_streaming(self):
        pass


class I_HarmonyAnalyzer(I_PitchStreamListener):
    @abstractmethod
    def new_pitches_detected(self, pitches: list[int]):
        pass


# Orchestrator
class ChordPredictor:
    def __init__(
        self, pitch_streamer: I_PitchStreamer, harmony_analyzer: I_HarmonyAnalyzer
    ):
        self.harmony_analyzer = harmony_analyzer
        self.pitch_streamer = pitch_streamer

    def run(self):
        self.pitch_streamer.start_streaming(stream_listener=self.harmony_analyzer)
        print("Started Pitch-Detecting Audio Streamer.  Press Enter to stop...")
        input()
        self.pitch_streamer.stop_streaming()
        print("Stopped Pitch-Detecting Audio Streamer.")
