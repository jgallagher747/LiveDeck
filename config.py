import os
import json

# Base directory (root of the project)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to assets and configuration files
SONG_DB_PATH = os.path.join(BASE_DIR, "config", "songs.json")
FONT_PATH = os.path.join(BASE_DIR, "assets", "DepartureMono-Regular.otf")
STOP_ICON_PATH = os.path.join(BASE_DIR, "assets", "stop.png")

# Stream Deck settings
STREAMDECK_BRIGHTNESS = 50  # Default brightness level

def load_songs():
    """
    Loads the song database from `songs.json`.

    Returns:
        dict: Dictionary containing the playlist data.
    """
    if not os.path.exists(SONG_DB_PATH):
        print("Warning: songs.json not found. Creating an empty playlist.")
        return {"playlist": []}  # Return an empty list if the file doesn't exist

    with open(SONG_DB_PATH, "r") as file:
        return json.load(file)

# Load song data at startup
SONG_DATA = load_songs()