"""
Thanks google gemini for writing my UI for me 👉👈
"""

from queue import Queue
from dataclasses import dataclass
import math

import customtkinter as ctk

from harmony_domain import HarmonyState, Note, NoteName, Chord, ChordType
from app import I_HarmonyPresenter

# Global settings for the app appearance
ctk.set_appearance_mode("system")  # Automatically matches OS theme
ctk.set_default_color_theme("blue")

FONT = "Nunito"


class TkinterAdapter(I_HarmonyPresenter):
    def __init__(self):
        self.state_update_queue = Queue()
        self.ui = TkinterUi(self.state_update_queue)

    def update_harmony_state(self, state: HarmonyState):
        self.state_update_queue.put(state)
        self.ui.event_generate("<<StateUpdate>>", when="tail")

    def run_ui_until_stopped_by_user(self):
        self.ui.mainloop()


class CircleDisplay(ctk.CTkFrame):
    """A reusable frame that draws 12 circles in a ring."""

    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)

        self.title_text = title
        self.text_ids = []
        self.circle_ids = []
        self.currently_highlighted_circle_indices = []
        self.default_circle_colour = "#43484c"

        # Create a canvas to draw circles
        # bg_color matches the frame, highlightthickness=0 removes border
        self.canvas = ctk.CTkCanvas(
            self,
            bg=self._apply_appearance_mode(self.cget("fg_color")),
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Redraw circles whenever the window is resized
        self.canvas.bind("<Configure>", self.draw_clock_circles)

    def draw_clock_circles(self, event=None):
        self.canvas.delete("all")

        # Get current dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        center_x = width / 2
        center_y = height / 2
        radius = min(center_x, center_y) * 0.7  # Size of the big ring
        circle_size = 30  # Size of each small circle

        self.canvas.create_text(
            center_x,
            center_y,
            text=self.title_text,  # Assuming you store the title
            font=(FONT, 24, "bold"),
            fill="white" if ctk.get_appearance_mode() == "Dark" else "black",
        )
        for i in range(12):
            # Calculate angle for each of the 12 circles (30 degrees apart)
            # Subtracting pi/2 starts the first circle at the top (12 o'clock)
            angle = (i * (360 / 12)) * (math.pi / 180) - (math.pi / 2)

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # Draw the circle
            circle_id = self.canvas.create_oval(
                x - circle_size,
                y - circle_size,
                x + circle_size,
                y + circle_size,
                fill=self.default_circle_colour,
                outline="grey",
                width=2,
            )
            t_id = self.canvas.create_text(
                x, y, text="", font=(FONT, 10), fill="#36454F"
            )
            self.text_ids.append(t_id)
            self.circle_ids.append(circle_id)

    def clear_text(self):
        for highlighted_index in self.currently_highlighted_circle_indices:
            self.canvas.itemconfig(self.text_ids[highlighted_index], text="")
            self.canvas.itemconfig(
                self.circle_ids[highlighted_index], fill=self.default_circle_colour
            )

        self.currently_highlighted_circle_indices.clear()

    def update_circle(self, index: int, new_text: str, colour: str, text_colour: str):
        self.currently_highlighted_circle_indices.append(index)
        self.canvas.itemconfig(self.circle_ids[index], fill=colour)
        self.canvas.itemconfig(self.text_ids[index], text=new_text, fill=text_colour)


class Formatter:
    @dataclass
    class ColourScheme:
        fill_colour: str
        text_colour: str

    def __init__(self):
        self.chord_type_to_str_map = {
            ChordType.MAJOR: "",
            ChordType.SEVENTH: "⁷",
            ChordType.MINOR: "m",
            ChordType.MIN_SEVENTH: "m⁷",
            ChordType.DIMINISHED: "°",
            ChordType.DIM_SEVENTH: "°⁷",
        }
        self.note_name_to_base_semitones_map = {
            NoteName.A: 9,
            NoteName.B: 11,
            NoteName.C: 0,
            NoteName.D: 2,
            NoteName.E: 4,
            NoteName.F: 5,
            NoteName.G: 7,
        }
        self.note_name_to_colour_map = {
            NoteName.A: self.ColourScheme(fill_colour="#C6AF83", text_colour="#43484c"),
            NoteName.B: self.ColourScheme(fill_colour="#00FFE5", text_colour="#43484c"),
            NoteName.C: self.ColourScheme(fill_colour="#FFFFFF", text_colour="#43484c"),
            NoteName.D: self.ColourScheme(fill_colour="#FFEA00", text_colour="#43484c"),
            NoteName.E: self.ColourScheme(fill_colour="#AB3553", text_colour="#ffffff"),
            NoteName.F: self.ColourScheme(fill_colour="#277C43", text_colour="#ffffff"),
            NoteName.G: self.ColourScheme(fill_colour="#6F4E37", text_colour="#ffffff"),
        }

    def format_note_to_string(self, note: Note):
        note_accidental = ""
        accidental_count = note.accidentals
        if accidental_count > 0:
            note_accidental = "♯" * accidental_count
        elif accidental_count < 0:
            note_accidental = "♭" * (-1 * accidental_count)
        return f"{note.note_name.name}{note_accidental}"

    def format_chord_to_string(self, chord: Chord):
        chord_root_name = self.format_note_to_string(chord.root)
        chord_str = f"{chord_root_name}{self.chord_type_to_str_map[chord.chord_type]}"
        return chord_str

    def convert_note_to_wrapped_semitones(self, note: Note):
        base_semitones = self.note_name_to_base_semitones_map[note.note_name]
        semitones_after_accidentals = base_semitones + note.accidentals
        return semitones_after_accidentals % 12

    def convert_note_to_position_on_circle_of_fifths(self, note: Note):
        wrapped_semitones = self.convert_note_to_wrapped_semitones(note)
        return (7 * wrapped_semitones) % 12

    def get_colour_for_note(self, note: Note):
        return self.note_name_to_colour_map[note.note_name]


class TkinterUi(ctk.CTk):
    def __init__(self, state_update_queue: Queue[HarmonyState]):
        super().__init__()

        self.formatter = Formatter()

        self.state_update_queue = state_update_queue
        self.harmony_state = None
        self.bind("<<StateUpdate>>", self.update_state)

        # Configure window
        self.title("Harmony Dashboard")
        self.geometry("1300x1000")

        # Configure the grid: 2 columns and 2 rows
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top section
        self.scale_view = CircleDisplay(self, title="Scale")
        self.scale_view.grid(
            row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
        )

        # Bottom Left
        self.chord_view = CircleDisplay(self, title="Chord")
        self.chord_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Bottom Right
        self.notes_view = CircleDisplay(self, title="Notes")
        self.notes_view.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    def update_state(self, event):
        new_harmony_state = self.state_update_queue.get()
        if new_harmony_state:
            new_scale = new_harmony_state.current_major_scale
            no_scale_cached = (
                self.harmony_state is None
                or self.harmony_state.current_major_scale is None
            )
            if new_scale and (
                no_scale_cached or new_scale != self.harmony_state.current_major_scale
            ):
                self.scale_view.clear_text()
                scale_str = self.formatter.format_note_to_string(new_scale)
                index_in_circle = (
                    self.formatter.convert_note_to_position_on_circle_of_fifths(
                        new_scale
                    )
                )
                colour_scheme = self.formatter.get_colour_for_note(new_scale)
                self.scale_view.update_circle(
                    index=index_in_circle,
                    new_text=scale_str,
                    colour=colour_scheme.fill_colour,
                    text_colour=colour_scheme.text_colour,
                )
            new_chord = new_harmony_state.current_chord
            no_chord_cached = (
                self.harmony_state is None or self.harmony_state.current_chord is None
            )
            if new_chord and (
                no_chord_cached or new_chord != self.harmony_state.current_chord
            ):
                self.chord_view.clear_text()
                chord_str = self.formatter.format_chord_to_string(new_chord)
                index_in_circle = (
                    self.formatter.convert_note_to_position_on_circle_of_fifths(
                        new_chord.root
                    )
                )
                colour_scheme = self.formatter.get_colour_for_note(new_chord.root)
                self.chord_view.update_circle(
                    index=index_in_circle,
                    new_text=chord_str,
                    colour=colour_scheme.fill_colour,
                    text_colour=colour_scheme.text_colour,
                )

            self.notes_view.clear_text()
            for note in new_harmony_state.notes_detected:
                note_str = self.formatter.format_note_to_string(note)
                index_in_circle = self.formatter.convert_note_to_wrapped_semitones(note)
                colour_scheme = self.formatter.get_colour_for_note(note)
                self.notes_view.update_circle(
                    index=index_in_circle,
                    new_text=note_str,
                    colour=colour_scheme.fill_colour,
                    text_colour=colour_scheme.text_colour,
                )
            self.harmony_state = new_harmony_state


if __name__ == "__main__":
    adapter = TkinterAdapter()
    print("Testing UI only...")
    adapter.run_ui_until_stopped_by_user()
