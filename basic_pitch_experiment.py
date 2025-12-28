from basic_pitch.inference import predict, Model
from basic_pitch import ICASSP_2022_MODEL_PATH

import sounddevice as sd
import threading
import soundfile as sf
import pretty_midi
import time
import queue
import numpy as np
import sys

# Configuration parameters
print_debug = False
samplerate = 22050  # Sample rate used by basic pitch
channels = 1  # Mono input
subtype = "PCM_16"
filename = "./temp.wav"
processing_period_seconds = 0.2
q = queue.Queue()
basic_pitch_model = Model(ICASSP_2022_MODEL_PATH)


def callback(indata, frames, time, status):
    """This function is called (from a separate thread) for each audio block."""
    if status:
        print(f"Status flags: {status}", file=sys.stderr)

    # Process the audio data here. 'indata' is a NumPy array of float32 samples.
    q.put(indata.copy())


thread_event = threading.Event()


def processing_worker():
    disk_write_time = 0
    while not thread_event.is_set():
        processing_start_time = time.time()
        arrs = []
        while not q.empty():
            arrs.append(
                q.get()
            )  # grab all the blocks until there's no more.  Pray that we do this faster than the stream puts blocks in there
        if arrs:
            block = np.concatenate(arrs, axis=0)
            # Write the block of of sound to disk
            with sf.SoundFile(
                filename,
                mode="w",
                samplerate=samplerate,
                channels=channels,
                subtype=subtype,
            ) as file:
                file.write(block)
            # Make basic pitch read it back out of disk (sigh)
            disk_write_time = time.time() - processing_start_time
            model_output, midi_data, note_events = predict(
                audio_path=filename,
                model_or_model_path=basic_pitch_model,
                minimum_frequency=27.5,
                maximum_frequency=2093.0,
            )
            # Print out detected notes
            if len(midi_data.instruments) > 0:
                instrument = midi_data.instruments[0]
                for note in instrument.notes:
                    note_name = pretty_midi.note_number_to_name(note.pitch)
                    print(
                        f"  Pitch: {note.pitch} ({note_name}), Velocity: {note.velocity}, Start: {note.start:.2f}s, End: {note.end:.2f}s"
                    )
        if print_debug:
            print(f"Disk writing took {disk_write_time} s")
            processing_time = time.time() - processing_start_time
            print(f"Processing took {processing_time} s")
        time.sleep(processing_period_seconds)


# Start processing_worker thread
processing_thread = threading.Thread(target=processing_worker)
processing_thread.start()
try:
    print(f"Recording. Press Enter to stop...")
    with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
        # The 'with' statement manages the stream; it runs in the background.
        # The main thread can do other things or simply wait.
        input()  # Wait for user input to stop the stream
except KeyboardInterrupt:
    print("\nRecording killed by user.")

except Exception as e:
    print(f"An error occurred: {e}")
print("Session ended by user")
thread_event.set()
processing_thread.join()
