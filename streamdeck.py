# --- streamdeck.py ---
import os
import json
import logging
import psutil
import time
import platform
import subprocess
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from config import SONG_DB_PATH, load_json
from controller import on_button_pressed, update_buttons

logging.basicConfig(level=logging.INFO)

SONG_DATA = load_json(SONG_DB_PATH, {"songs": []})


def close_streamdeck_app():
    """Close the StreamDeck application if it's running"""
    # Very specific StreamDeck process names
    streamdeck_names = {
        'Stream Deck',  # macOS app name
        'StreamDeck',   # Windows app name
        'streamdeck'    # Linux app name
    }
    terminated = False

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Get process name and ensure it's a string
            proc_name = str(proc.info['name']).strip()
            
            # Exact match only
            if proc_name in streamdeck_names:
                logging.info(f"Found StreamDeck app: {proc_name} (PID: {proc.pid})")
                proc.terminate()
                terminated = True
                logging.info(f"Terminated StreamDeck app process")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.debug(f"Process access error: {e}")
            continue

    if terminated:
        time.sleep(1)  # Reduced wait time


def initialize_streamdeck():
    """Initialize StreamDeck by closing any running instance and starting a new one."""
    logging.info("Starting StreamDeck initialization...")
    
    # Close StreamDeck app
    close_streamdeck_app()

    # Initialize device
    manager = DeviceManager()
    streamdecks = manager.enumerate()
    if not streamdecks:
        logging.warning("No Stream Deck devices found.")
        return None

    deck = streamdecks[0]
    deck.open()
    logging.info(f"Connected to Stream Deck: {deck.deck_type()}")
    update_buttons(deck)
    deck.set_key_callback(on_button_pressed)
    logging.info("Stream Deck initialized successfully")
    return deck


if __name__ == "__main__":
    deck = initialize_streamdeck()
    if deck:
        logging.info("Listening for Stream Deck events...")
        while True:
            pass