from abc import ABC, abstractmethod

from harmony_domain import HarmonyState


# Interfaces
class I_PitchStreamListener(ABC):
    """
    Callback to be passed into an I_PitchStreamer.
    """

    @abstractmethod
    def new_pitches_detected(self, pitches: list[int]):
        """
        pitches in midi numbers
        """
        pass


class I_PitchStreamer(ABC):
    """
    Expected to stream audio, sampling that stream at a relatively high frequency to
    detect individual pitches.  Should notify the listener in real time
    with those pitches as they are detected.
    """

    @abstractmethod
    def register_listener(self, stream_listener: I_PitchStreamListener):
        pass

    @abstractmethod
    def start_streaming(self):
        pass

    @abstractmethod
    def stop_streaming(self):
        pass


class I_HarmonyStateListener(ABC):
    """
    Callback to be passed into an I_HarmonyAnalyzer
    """

    @abstractmethod
    def update_harmony_state(self, state: HarmonyState):
        pass


class I_HarmonyAnalyzer(I_PitchStreamListener):
    """
    Analyzes pitches as they are detected, generates a 'HarmonyState'
    based on those pitches, then updates the listener with that state.
    """

    @abstractmethod
    def register_listener(self, listener: I_HarmonyStateListener):
        pass


class I_HarmonyPresenter(I_HarmonyStateListener):
    """
    Expected to present the current harmony state on a UI.
    """

    @abstractmethod
    def run_ui_until_stopped_by_user(self):
        pass


class App:
    def __init__(
        self,
        pitch_streamer: I_PitchStreamer,
        harmony_analyzer: I_HarmonyAnalyzer,
        presenter: I_HarmonyPresenter,
    ):
        self.pitch_streamer = pitch_streamer
        self.harmony_analyzer = harmony_analyzer
        self.presenter = presenter

        self.pitch_streamer.register_listener(self.harmony_analyzer)
        self.harmony_analyzer.register_listener(self.presenter)

    def run(self):
        self.pitch_streamer.start_streaming()
        print("Started Pitch-Detecting Audio Streamer.")
        self.presenter.run_ui_until_stopped_by_user()
        self.pitch_streamer.stop_streaming()
        print("Stopped Pitch-Detecting Audio Streamer.")
