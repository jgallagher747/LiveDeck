# --- streamdeck.py ---
import os
import json
import logging
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from config import SONG_DB_PATH, load_json
from controller import on_button_pressed, update_buttons

logging.basicConfig(level=logging.INFO)

SONG_DATA = load_json(SONG_DB_PATH, {"songs": []})


def initialize_streamdeck():
    """Initializes the Stream Deck device."""
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
    return deck

if __name__ == "__main__":
    deck = initialize_streamdeck()
    if deck:
        logging.info("Listening for Stream Deck events...")
        while True:
            pass

