import os
import json
import logging
import time
import mido
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper
from ableton import play_track, stop_all
from config import BASE_DIR, SONG_DB_PATH, load_json

logging.basicConfig(level=logging.INFO)

# MIDI Note Mapping remains unchanged
MIDI_NOTE_MAP = {
    "C": 37, "C#": 38, "D": 39, "D#": 40, "E": 41, "F": 42, "F#": 43,
    "G": 44, "G#": 45, "A": 46, "A#": 47, "B": 48
}

class Controller:
    SONGS_PER_PAGE = 7       # Main keys 0-6 for songs
    STOP_BUTTON_INDEX = 7    # Main key 7 for the stop button
    NAV_BACK_INDEX = 8       # Touch key for previous page
    NAV_FORWARD_INDEX = 9    # Touch key for next page

    # Cache for raw icon images and final rendered button images
    icon_cache = {}
    button_image_cache = {}

    @staticmethod
    def get_key_size(deck):
        fmt = deck.key_image_format()
        if hasattr(fmt, "get"):
            key_size = fmt.get("size")
            if key_size is not None:
                return tuple(key_size)
        return tuple(fmt)

    def __init__(self, outport):
        self.outport = outport
        self.song_data = load_json(SONG_DB_PATH).get("songs", [])
        self.current_page = 0
        logging.info("Loaded song data: %s", json.dumps(self.song_data, indent=2))
        self.artwork_path = "assets/artwork"
        self.font_path = os.path.join(BASE_DIR, "assets", "DepartureMono-Regular.otf")
        self.font = ImageFont.truetype(self.font_path, 14)

    def load_icon(self, icon_path, key_size):
        """Load an icon from disk using cache."""
        if icon_path in Controller.icon_cache:
            return Controller.icon_cache[icon_path]
        try:
            icon = Image.open(icon_path).convert("RGBA")
        except FileNotFoundError:
            logging.warning("Image not found: %s, using default.", icon_path)
            icon = Image.new("RGBA", key_size, (0, 0, 0, 0))
        Controller.icon_cache[icon_path] = icon
        return icon

    def pre_render_all_buttons(self, deck):
        """
        Pre-render and cache all button images for the entire song list.
        This should be called once after the deck is initialized.
        """
        key_size = Controller.get_key_size(deck)
        for song in self.song_data:
            cache_key = song.get("id", song.get("title", "unknown"))
            if cache_key not in Controller.button_image_cache:
                icon_path = os.path.join(BASE_DIR, song.get("image", ""))
                icon = self.load_icon(icon_path, key_size)
                image = PILHelper.create_scaled_key_image(deck, icon)
                draw = ImageDraw.Draw(image)
                draw.rectangle((0, 64, 96, 96), fill=(0, 0, 0))
                draw.text((image.width / 2, image.height - 10),
                          song.get("title", ""),
                          font=self.font, anchor="ms", fill="white")
                native_img = PILHelper.to_native_key_format(deck, image)
                Controller.button_image_cache[cache_key] = native_img
        logging.info("Pre-rendered %d button images", len(Controller.button_image_cache))

    def render_button(self, deck, song):
        """
        Generate a button image for a song.
        This method is only used as a fallback if a song isn't pre-rendered.
        """
        key_size = Controller.get_key_size(deck)
        cache_key = song.get("id", song.get("title", "unknown"))
        if cache_key in Controller.button_image_cache:
            return Controller.button_image_cache[cache_key]

        icon_path = os.path.join(BASE_DIR, song.get("image", ""))
        icon = self.load_icon(icon_path, key_size)
        image = PILHelper.create_scaled_key_image(deck, icon)
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 64, 96, 96), fill=(0, 0, 0))
        draw.text((image.width / 2, image.height - 10),
                  song.get("title", ""),
                  font=self.font, anchor="ms", fill="white")
        native_img = PILHelper.to_native_key_format(deck, image)
        Controller.button_image_cache[cache_key] = native_img
        return native_img

    def update_buttons(self, deck):
        """
        Update the buttons on the device.
        Main keys 0-6: Song buttons.
        Key 7: Stop button.
        Keys 8 and 9: Navigation indicators.
        """
        key_size = Controller.get_key_size(deck)
        total_pages = (len(self.song_data) + Controller.SONGS_PER_PAGE - 1) // Controller.SONGS_PER_PAGE
        start_index = self.current_page * Controller.SONGS_PER_PAGE

        # Update song buttons (keys 0-6)
        for key in range(Controller.SONGS_PER_PAGE):
            song_index = start_index + key
            if song_index < len(self.song_data):
                song = self.song_data[song_index]
                cache_key = song.get("id", song.get("title", "unknown"))
                native_img = Controller.button_image_cache.get(cache_key)
                if native_img is None:
                    native_img = self.render_button(deck, song)
            else:
                placeholder = Image.new("RGBA", key_size, (50, 50, 50))
                scaled = PILHelper.create_scaled_key_image(deck, placeholder)
                native_img = PILHelper.to_native_key_format(deck, scaled)
            deck.set_key_image(key, native_img)

        # Stop button on key 7
        stop_icon_path = os.path.join(BASE_DIR, "assets", "stop.png")
        try:
            stop_icon = Image.open(stop_icon_path).convert("RGBA")
        except FileNotFoundError:
            stop_icon = Image.new("RGBA", key_size, (255, 0, 0))
        scaled = PILHelper.create_scaled_key_image(deck, stop_icon)
        native_img = PILHelper.to_native_key_format(deck, scaled)
        deck.set_key_image(Controller.STOP_BUTTON_INDEX, native_img)

        # Navigation indicators on keys 8 and 9
        if self.current_page > 0:
            deck.set_key_color(Controller.NAV_BACK_INDEX, 255, 255, 255)
        else:
            deck.set_key_color(Controller.NAV_BACK_INDEX, 0, 0, 0)

        if self.current_page < total_pages - 1:
            deck.set_key_color(Controller.NAV_FORWARD_INDEX, 255, 255, 255)
        else:
            deck.set_key_color(Controller.NAV_FORWARD_INDEX, 0, 0, 0)

    def handle_button_press(self, deck, key, state):
        """Handle key presses for song selection, stopping, and page navigation."""
        total_pages = (len(self.song_data) + Controller.SONGS_PER_PAGE - 1) // Controller.SONGS_PER_PAGE
        if not state:
            return  # Process only key down events

        if key == Controller.STOP_BUTTON_INDEX:
            logging.info("Stop button pressed.")
            stop_all()
            self.update_buttons(deck)
        elif key == Controller.NAV_BACK_INDEX and self.current_page > 0:
            logging.info("Navigating to previous page.")
            self.current_page -= 1
            self.update_buttons(deck)
        elif key == Controller.NAV_FORWARD_INDEX and self.current_page < total_pages - 1:
            logging.info("Navigating to next page.")
            self.current_page += 1
            self.update_buttons(deck)
        elif key < Controller.SONGS_PER_PAGE:
            song_index = self.current_page * Controller.SONGS_PER_PAGE + key
            if song_index < len(self.song_data):
                song = self.song_data[song_index]
                logging.info("Playing song: %s", song.get("title", "Unknown"))
                stop_all()
                play_track(song.get("ableton_track"))
                self.send_midi_key(song.get("key"))
                self.update_buttons(deck)

    def send_midi_key(self, song_key):
        """Convert song key to MIDI note and send it."""
        if song_key in MIDI_NOTE_MAP:
            adjusted_note = MIDI_NOTE_MAP[song_key] - 1
            msg = mido.Message("note_on", note=adjusted_note, velocity=64)
            self.outport.send(msg)
            time.sleep(0.1)
            self.outport.send(mido.Message("note_off", note=adjusted_note, velocity=64))
            logging.info(f"Sent MIDI note {adjusted_note} for key {song_key}")
        else:
            logging.warning(f"Invalid song key: {song_key}")