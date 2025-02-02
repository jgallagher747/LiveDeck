# --- config.py ---
import os
import json

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SONG_DB_PATH = os.path.join(BASE_DIR, "config", "songs.json")
FONT_PATH = os.path.join(BASE_DIR, "assets", "DepartureMono-Regular.otf")
STOP_ICON_PATH = os.path.join(BASE_DIR, "assets", "stop.png")
STREAMDECK_BRIGHTNESS = 50


def load_json(filepath, default=None):
    """Loads a JSON file and returns its content."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing required file: {filepath}")
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {filepath}: {e}")


SONG_DATA = load_json(SONG_DB_PATH, {"songs": []})