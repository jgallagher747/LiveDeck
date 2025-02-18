#!/usr/bin/env python3

# --- main.py ---

import time
import os
import logging
import mido
import threading
import console
from midi import forward_midi
from controller import Controller
from streamdeck import initialize_streamdeck
from config import BASE_DIR
from ableton import ableton, ABLETON_SET_PATH

# Get the script's actual location (the LiveDeck project root)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(BASE_DIR)

ARTWORK_PATH = "assets/artwork"  # Update if needed

def init():
    os.makedirs(ARTWORK_PATH, exist_ok=True)

def init_midi_outport():
    midi_output_name = "IAC Driver Bus 2"  # Adjust as needed
    return mido.open_output(midi_output_name)

def main():
    """Main function that initializes and runs the LiveDeck application."""

    # Start the MIDI forwarding loop in a daemon thread
    midi_thread = threading.Thread(target=forward_midi, daemon=True)
    midi_thread.start()

    os.chdir(BASE_DIR)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize the MIDI output port and create a Controller instance with it
    outport = init_midi_outport()
    controller = Controller(outport)
    
    # Launch and connect to Ableton
    logging.info("Initializing Ableton Live...")
    if not ableton.launch_set(ABLETON_SET_PATH):
        logging.error("Failed to launch Ableton Live. Exiting.")
        return
        
    if not ableton.connect_to_set():
        logging.error("Failed to connect to Ableton Live set. Exiting.")
        return
    
    # Initialize StreamDeck
    logging.info("Initializing Stream Deck...")
    deck = initialize_streamdeck()
    if not deck:
        logging.error("Failed to initialize Stream Deck. Exiting.")
        return
    
    # Pre-render all buttons
    controller.pre_render_all_buttons(deck)


    # Start info bar update loop
    controller.start_info_bar_update(deck)

    # Launch UAD Console
    console.uad_launch()

    # Register Controller's method as the callback for key events.
    deck.set_key_callback(lambda d, key, state: controller.handle_button_press(d, key, state))
    controller.update_buttons(deck)
    
    try:
        logging.info("LiveDeck running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down LiveDeck...")
        deck.reset()
        deck.close()
        logging.info("Shutdown complete.")

if __name__ == "__main__":
    main()