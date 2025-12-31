from queue import Queue

import customtkinter

from harmony_domain import HarmonyState, Note
from app import I_HarmonyPresenter

# Global settings for the app appearance
customtkinter.set_appearance_mode("system")  # Automatically matches OS theme
customtkinter.set_default_color_theme("blue")


class TkinterAdapter(I_HarmonyPresenter):
    def __init__(self):
        self.state_update_queue = Queue()
        self.ui = TkinterUi(self.state_update_queue)

    def update_harmony_state(self, state: HarmonyState):
        self.state_update_queue.put(state)
        self.ui.event_generate("<<StateUpdate>>", when="tail")

    def run_ui_until_stopped_by_user(self):
        self.ui.mainloop()


class TkinterUi(customtkinter.CTk):
    def __init__(self, state_update_queue: Queue[HarmonyState]):
        super().__init__()

        self.state_update_queue = state_update_queue
        self.harmony_state = None
        self.bind("<<StateUpdate>>", self.update_state)

        # Configure window
        self.title("Harmony Dashboard")
        self.geometry("1000x800")

        self.label = customtkinter.CTkLabel(self, text="listening")
        self.label.pack(pady=20, padx=20)

    def update_state(self, event):
        self.harmony_state = self.state_update_queue.get()
        if self.harmony_state:
            current_scale = self.harmony_state.current_major_scale
            scale_str = ""
            if current_scale:
                scale_str = "Major Scale: " + self._format_note_to_string(current_scale)

            chord_str = ""
            current_chord = self.harmony_state.current_chord
            if current_chord:
                chord_root_name = self._format_note_to_string(current_chord.root)
                chord_str = f"Chord: {chord_root_name} {current_chord.chord_type.name}"
            notes_as_str = ", ".join(
                [
                    self._format_note_to_string(note)
                    for note in self.harmony_state.notes_detected
                ]
            )
            notes_str = "Notes: " + notes_as_str
            self.label.configure(text=scale_str + " | " + chord_str + " | " + notes_str)

    def _format_note_to_string(self, note: Note):
        note_accidental = ""
        accidental_count = note.accidentals
        if accidental_count > 0:
            note_accidental = "#" * accidental_count
        elif accidental_count < 0:
            note_accidental = "b" * (-1 * accidental_count)
        return f"{note.note_name.name}{note_accidental}"
