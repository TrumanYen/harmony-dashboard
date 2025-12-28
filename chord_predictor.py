from real_time_basic_pitch import PitchDetectingAudioStreamer, I_PitchStreamListener


class DummyPitchListener(I_PitchStreamListener):
    def new_pitches_detected(self, pitches: list[int]):
        print(pitches)


class ChordPredictor:
    def __init__(self):
        self.listener = DummyPitchListener()
        self.pitch_detecting_audio_streamer = PitchDetectingAudioStreamer(self.listener)

    def run(self):
        self.pitch_detecting_audio_streamer.start_streaming()
        print("Started Pitch-Detecting Audio Streamer.  Press Enter to stop...")
        input()
        self.pitch_detecting_audio_streamer.stop_streaming()


if __name__ == "__main__":
    chord_predictor = ChordPredictor()
    chord_predictor.run()
