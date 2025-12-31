from queue import Queue

import customtkinter as ctk

from harmony_domain import HarmonyState, Note
from app import I_HarmonyPresenter

# Global settings for the app appearance
ctk.set_appearance_mode("system")  # Automatically matches OS theme
ctk.set_default_color_theme("blue")


class TkinterAdapter(I_HarmonyPresenter):
    def __init__(self):
        self.state_update_queue = Queue()
        self.ui = TkinterUi(self.state_update_queue)

    def update_harmony_state(self, state: HarmonyState):
        self.state_update_queue.put(state)
        self.ui.event_generate("<<StateUpdate>>", when="tail")

    def run_ui_until_stopped_by_user(self):
        self.ui.mainloop()


class TkinterUi(ctk.CTk):
    def __init__(self, state_update_queue: Queue[HarmonyState]):
        super().__init__()

        self.state_update_queue = state_update_queue
        self.harmony_state = None
        self.bind("<<StateUpdate>>", self.update_state)

        # Configure window
        self.title("Harmony Dashboard")
        self.geometry("1000x800")

        # Configure the grid: 2 columns and 2 rows
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Scale Section (Top)
        self.scale_frame = ctk.CTkFrame(self)
        self.scale_frame.grid(
            row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="nsew"
        )
        self.scale_label = ctk.CTkLabel(
            self.scale_frame, text="Listening..", font=("Arial", 24)
        )
        self.scale_label.pack(expand=True)

        # 2. Chord Section (Bottom Left)
        self.chord_frame = ctk.CTkFrame(self)
        self.chord_frame.grid(
            row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="nsew"
        )
        self.chord_label = ctk.CTkLabel(
            self.chord_frame, text="Listening..", font=("Arial", 24)
        )
        self.chord_label.pack(expand=True)

        # 3. Notes Section (Bottom Right)
        self.notes_frame = ctk.CTkFrame(self)
        self.notes_frame.grid(
            row=1, column=1, padx=(5, 10), pady=(5, 10), sticky="nsew"
        )
        self.notes_label = ctk.CTkLabel(
            self.notes_frame, text="Listening..", font=("Arial", 24)
        )
        self.notes_label.pack(expand=True)

    def update_state(self, event):
        self.harmony_state = self.state_update_queue.get()
        if self.harmony_state:
            current_scale = self.harmony_state.current_major_scale
            scale_str = "?"
            if current_scale:
                scale_str = self._format_note_to_string(current_scale)

            chord_str = "?"
            current_chord = self.harmony_state.current_chord
            if current_chord:
                chord_root_name = self._format_note_to_string(current_chord.root)
                chord_str = f"{chord_root_name} {current_chord.chord_type.name}"
            notes_as_str = ", ".join(
                [
                    self._format_note_to_string(note)
                    for note in self.harmony_state.notes_detected
                ]
            )
            self.scale_label.configure(text="Major Scale: " + scale_str)
            self.chord_label.configure(text="Chord: " + chord_str)
            self.notes_label.configure(text="Notes: " + notes_as_str)

    def _format_note_to_string(self, note: Note):
        note_accidental = ""
        accidental_count = note.accidentals
        if accidental_count > 0:
            note_accidental = "#" * accidental_count
        elif accidental_count < 0:
            note_accidental = "b" * (-1 * accidental_count)
        return f"{note.note_name.name}{note_accidental}"


if __name__ == "__main__":
    adapter = TkinterAdapter()
    print("Testing UI only...")
    adapter.run_ui_until_stopped_by_user()
