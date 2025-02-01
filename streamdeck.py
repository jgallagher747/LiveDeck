# --- streamdeck.py ---
import os
import json
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from ableton import play_track, stop_all
from config import SONG_DB_PATH

# Load settings from settings file.
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "settings.json")
try:
    with open(SETTINGS_PATH, "r") as f:
        SETTINGS = json.load(f)
except Exception:
    SETTINGS = {"streamdeck": {"brightness": 50, "stop_button_index": -1}}

def load_songs():
    """
    Loads the song database from songs.json.
    """
    if not os.path.exists(SONG_DB_PATH):
        print("Warning: songs.json not found. Using empty playlist.")
        return []
    with open(SONG_DB_PATH, "r") as file:
        data = json.load(file)
    if isinstance(data, dict) and "songs" in data:
        return data["songs"]
    print("Warning: songs.json is not in the expected format. Using empty list.")
    return []

SONG_DATA = load_songs()

def initialize_streamdeck():
    """
    Initializes the Stream Deck device, updates button images, and sets up button callbacks.
    """
    manager = DeviceManager()
    streamdecks = manager.enumerate()
    if not streamdecks:
        print("No Stream Deck devices found.")
        return None
    deck = streamdecks[0]
    deck.open()
    deck.set_brightness(SETTINGS["streamdeck"].get("brightness", 50))
    print(f"Connected to Stream Deck: {deck.deck_type()}")
    
    update_buttons(deck)
    deck.set_key_callback(lambda d, k, s: on_button_pressed(d, k, s))
    return deck

def render_button(deck, song):
    """
    Generates a button image for a given song.
    """
    icon = Image.open(song["image"])
    image = PILHelper.create_scaled_key_image(deck, icon)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("assets/DepartureMono-Regular.otf", 14)
    draw.text((image.width / 2, image.height - 10), song["title"], font=font, anchor="ms", fill="white")
    return PILHelper.to_native_key_format(deck, image)

def update_buttons(deck):
    """
    Updates the Stream Deck buttons with song images.
    """
    for key, song in enumerate(SONG_DATA):
        image = render_button(deck, song)
        deck.set_key_image(key, image)
    
    # Assign the stop button to the last key.
    if SETTINGS["streamdeck"].get("stop_button_index", -1) == -1:
        stop_key = deck.key_count() - 1
    else:
        stop_key = SETTINGS["streamdeck"]["stop_button_index"]

    stop_icon = Image.open("assets/stop.png")
    stop_image = PILHelper.create_scaled_key_image(deck, stop_icon)
    stop_image_bytes = PILHelper.to_native_key_format(deck, stop_image)
    deck.set_key_image(stop_key, stop_image_bytes)

def on_button_pressed(deck, key, state):
    """
    Handles button presses on the Stream Deck.
    The stop button (reserved key) stops all playback via OSC.
    Other buttons play the corresponding track.
    """
    if state:  # Key pressed
        stop_button_index = SETTINGS["streamdeck"].get("stop_button_index", -1)
        if stop_button_index == -1:
            stop_button_index = deck.key_count() - 1

        if key == stop_button_index:
            print("Stop button pressed.")
            stop_all()
            update_buttons(deck)  # Refresh button images if needed
        elif key < len(SONG_DATA):
            song = SONG_DATA[key]
            print(f"Playing: {song['title']}")
            play_track(song["ableton_track"])
            update_buttons(deck)

if __name__ == "__main__":
    deck = initialize_streamdeck()
    if deck:
        print("Listening for Stream Deck events...")
        while True:
            pass