from chord_predictor import ChordPredictor
from real_time_basic_pitch import PitchDetectingAudioStreamer
from harmony_analyzer import HarmonyAnalyzer

if __name__ == "__main__":
    pitch_detecting_audio_streamer = PitchDetectingAudioStreamer()
    harmony_analyzer = HarmonyAnalyzer()

    chord_predictor = ChordPredictor(
        pitch_streamer=pitch_detecting_audio_streamer, harmony_analyzer=harmony_analyzer
    )

    chord_predictor.run()
