from app import App, I_HarmonyPresenter
from harmony_domain import HarmonyState, Note, Chord, ChordType
from real_time_basic_pitch import PitchDetectingAudioStreamer
from harmony_module import HarmonyModule


class DummyHarmonyPresenter(I_HarmonyPresenter):
    def update_harmony_state(self, state: HarmonyState):
        current_scale = state.current_major_scale
        scale_str = ""
        if current_scale:
            scale_str = "Major Scale: " + self._format_note_to_string(current_scale)

        chord_str = ""
        current_chord = state.current_chord
        if current_chord:
            chord_root_name = self._format_note_to_string(current_chord.root)
            chord_str = f"Chord: {chord_root_name} {current_chord.chord_type.name}"
        notes_as_str = ", ".join(
            [self._format_note_to_string(note) for note in state.notes_detected]
        )
        notes_str = "Notes: " + notes_as_str
        print(scale_str + " | " + chord_str + " | " + notes_str)

    def _format_note_to_string(self, note: Note):
        note_accidental = ""
        accidental_count = note.accidentals
        if accidental_count > 0:
            note_accidental = "#" * accidental_count
        elif accidental_count < 0:
            note_accidental = "b" * (-1 * accidental_count)
        return f"{note.note_name.name}{note_accidental}"

    def run_ui_until_stopped_by_user(self):
        pass


if __name__ == "__main__":
    pitch_detecting_audio_streamer = PitchDetectingAudioStreamer()
    harmony_analyzer = HarmonyModule()
    presenter = DummyHarmonyPresenter()  # TODO: use a real presenter

    app = App(
        pitch_streamer=pitch_detecting_audio_streamer,
        harmony_analyzer=harmony_analyzer,
        presenter=presenter,
    )

    app.run()
