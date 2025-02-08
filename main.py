#!/usr/bin/env python3

# --- main.py ---

import time
import os
import logging
from streamdeck import initialize_streamdeck
from config import BASE_DIR
from ableton import ableton, ABLETON_SET_PATH
from convert import convert_to_png

# Get the script's actual location (the LiveDeck project root)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(BASE_DIR)

# Update any direct artwork path references
ARTWORK_PATH = "assets/artwork"  # Update from "artwork" if it exists

def init():
    os.makedirs(ARTWORK_PATH, exist_ok=True)
    # ... rest of initialization ...

def main():
    """Main function that initializes and runs the LiveDeck application."""
    # Set working directory
    os.chdir(BASE_DIR)
    
    # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # #Convert all jpg to png
    # source_dir = os.path.join(BASE_DIR, "assets", "artwork")
    # target_dir = os.path.join(BASE_DIR, "assets", "artwork", "artwork_png")

    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(asctime)s - %(levelname)s - %(message)s'
    # )
    # logging.info("Converting images to PNG...")
    # convert_to_png(source_dir, target_dir)

    # logging.info("Finished conversion. Starting LiveDeck application...")

    # Launch and connect to Ableton
    logging.info("Initializing Ableton Live...")
    if not ableton.launch_set(ABLETON_SET_PATH):
        logging.error("Failed to launch Ableton Live. Exiting.")
        return
        
    # Connect to the Ableton set
    if not ableton.connect_to_set():
        logging.error("Failed to connect to Ableton Live set. Exiting.")
        return
    
    # Initialize StreamDeck
    logging.info("Initializing Stream Deck...")
    deck = initialize_streamdeck()
    if not deck:
        logging.error("Failed to initialize Stream Deck. Exiting.")
        return
    
    try:
        logging.info("LiveDeck running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)  # Keep script running efficiently
    except KeyboardInterrupt:
        logging.info("Shutting down LiveDeck...")
        deck.reset()
        deck.close()
        logging.info("Shutdown complete.")

if __name__ == "__main__":
    main()