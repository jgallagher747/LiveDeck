# --- midi.py ---

import mido
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# MIDI Note Mapping
MIDI_NOTE_MAP = {
    "C": 37, "C#": 38, "D": 39, "D#": 40, "E": 41, "F": 42, "F#": 43,
    "G": 44, "G#": 45, "A": 46, "A#": 47, "B": 48
}

# List available MIDI ports
logging.info("Available MIDI Inputs: %s", mido.get_input_names())
logging.info("Available MIDI Outputs: %s", mido.get_output_names())

# Define the MIDI input sources (Modify these based on your setup)
midi_inputs = [
    "Akai MPK88 Port 1",  # Change to match your MIDI controller's name
    "IAC Driver Bus 1"    # Virtual MIDI Bus
]

# Define the MIDI output (Aggregate destination)
midi_output_name = "IAC Driver Bus 2"  # Change to the desired virtual MIDI output
outport = mido.open_output(midi_output_name)

# Default listen range
listen_range = (0, 128)  # A0 to C8 (MIDI Note Numbers)

# Function to set the listen range dynamically
def set_listen_range(low, high):
    global listen_range
    listen_range = (low, high)
    logging.info("Updated Listen Range: %s", listen_range)

# Function to forward and process incoming MIDI with filtering
def forward_midi():
    try:
        with mido.open_input(midi_inputs[0]) as inport1, mido.open_input(midi_inputs[1]) as inport2:
            logging.info("Listening on %s and sending to %s", midi_inputs, midi_output_name)

            while True:
                for inport in [inport1, inport2]:
                    for msg in inport.iter_pending():
                        if msg.type in ["note_on", "note_off"]:
                            if listen_range[0] <= msg.note <= listen_range[1]:
                                # Log a copy of the message with note incremented by 1
                                logging.info("Forwarding: %s", msg.copy(note=msg.note+1))
                                outport.send(msg)  # Send only within range
                            else:
                                logging.info("Ignored: %s", msg.note)
                        else:
                            outport.send(msg)  # Forward non-note messages
                time.sleep(0.1)            
    except KeyboardInterrupt:
        logging.info("MIDI Routing Stopped")

# Example Usage: Update listen range dynamically
set_listen_range(21, 108)  # A0 to C8

if __name__ == "__main__":
    forward_midi()