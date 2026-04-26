from dataclasses import dataclass
from collections import deque
import csv
import time
import threading
from pathlib import Path

from .app import I_HarmonyPresenter
from .harmony_domain import HarmonyState, NoteName, ChordType


@dataclass
class TimestampedHarmonyState:
    time_since_start_ms: int
    harmony_state: HarmonyState


class HarmonyStateLogger:
    def __init__(self, log_output_path: str):
        self.output_path = log_output_path
        self.state_queue: deque[TimestampedHarmonyState] = deque([])
        self.most_recent_state: HarmonyState | None = (
            None  # Separately keep track of this because the queue gets emptied by the background thread regularly
        )
        self.start_time = self._current_time_ms()
        self._initialize_log()
        self.note_name_to_str_map = {
            NoteName.A: "A",
            NoteName.B: "B",
            NoteName.C: "C",
            NoteName.D: "D",
            NoteName.E: "E",
            NoteName.F: "F",
            NoteName.G: "G",
        }
        self.chord_type_to_str_map = {
            ChordType.MAJOR: "MAJ",
            ChordType.MINOR: "MIN",
            ChordType.DIMINISHED: "DIM",
            ChordType.SEVENTH: "7",
            ChordType.MIN_SEVENTH: "MIN_7",
            ChordType.MAJ_SEVENTH: "MAJ_7",
            ChordType.DIM_SEVENTH: "DIM_7",
        }
        self.threading_event = threading.Event()
        self.disk_writing_thread = threading.Thread(
            target=self._periodically_write_to_disk
        )
        self.disk_writing_thread.start()

    def log_harmony_state(self, state: HarmonyState):
        # Don't care about note detection, only chord and scale changes
        state_changed = True
        if self.most_recent_state:
            state_changed = (
                state.current_major_scale != self.most_recent_state.current_major_scale
                or state.current_chord != self.most_recent_state.current_chord
            )
        if state_changed:
            self.state_queue.append(
                TimestampedHarmonyState(
                    time_since_start_ms=(self._current_time_ms() - self.start_time),
                    harmony_state=state,
                )
            )
            self.most_recent_state = state

    def stop_logging(self):
        self.threading_event.set()
        self.disk_writing_thread.join()

    def _periodically_write_to_disk(self):
        LOG_UPDATE_PERIOD_S = 1
        with open(self.output_path, "a", newline="") as f:
            writer = csv.writer(f)
            while not self.threading_event.is_set():
                time.sleep(LOG_UPDATE_PERIOD_S)
                while len(self.state_queue) > 0:
                    state = self.state_queue.popleft()
                    maj_scale = state.harmony_state.current_major_scale
                    chord = state.harmony_state.current_chord
                    row = [
                        str(state.time_since_start_ms),
                        self._convert_note_name_to_string(maj_scale.note_name)
                        if maj_scale
                        else "",
                        str(maj_scale.accidentals) if maj_scale else "",
                        self._convert_note_name_to_string(chord.root.note_name)
                        if chord
                        else "",
                        str(chord.root.accidentals) if chord else "",
                        self._convert_chord_type_to_string(chord.chord_type)
                        if chord
                        else "",
                    ]
                    writer.writerow(row)

    def _convert_note_name_to_string(self, note_name: NoteName) -> str:
        return (
            self.note_name_to_str_map[note_name]
            if note_name in self.note_name_to_str_map.keys()
            else ""
        )

    def _convert_chord_type_to_string(self, chord_type: ChordType) -> str:
        return (
            self.chord_type_to_str_map[chord_type]
            if chord_type in self.chord_type_to_str_map.keys()
            else ""
        )

    def _initialize_log(self):
        assert not Path(self.output_path).exists(), "ERROR: Log file already exists"
        HEADER = [
            "timeSinceStartMs",
            "majScaleRootNote",
            "majScaleRootAccidentalNum",
            "chordRootNote",
            "chordRootAccidentalNum",
            "chordType",
        ]
        with open(self.output_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)

    def _current_time_ms(self) -> int:
        return int(time.time() * 1e3)


class LoggingHarmonyPresenterDecorator(I_HarmonyPresenter):
    def __init__(self, underlying_presenter: I_HarmonyPresenter, log_path: str):
        self.underlying_presenter = underlying_presenter
        self.logger = HarmonyStateLogger(log_output_path=log_path)

    def update_harmony_state(self, state: HarmonyState):
        self.logger.log_harmony_state(state)
        self.underlying_presenter.update_harmony_state(state)

    def run_ui_until_stopped_by_user(self):
        self.underlying_presenter.run_ui_until_stopped_by_user()
        self.logger.stop_logging()


# TODO: We can make an implementation of I_HarmonyPresenter that will only log.  But this will require
# something to tell it when to stop logging (e.g. a callback wired from the playback system?)
