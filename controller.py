import os
import json
import logging
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper
from ableton import play_track, stop_all
from config import BASE_DIR, SONG_DB_PATH, load_json

logging.basicConfig(level=logging.INFO)

class Controller:
    SONGS_PER_PAGE = 7       # Main keys 0-6 for songs
    STOP_BUTTON_INDEX = 7    # Main key 7 for the stop button
    NAV_BACK_INDEX = 8       # Touch key for previous page
    NAV_FORWARD_INDEX = 9    # Touch key for next page

    @staticmethod
    def get_key_size(deck):
        """
        Returns the key size as a tuple (width, height).
        For StreamDeckNeo, deck.key_image_format() returns a dict with a "size" key.
        """
        fmt = deck.key_image_format()
        if hasattr(fmt, "get"):
            key_size = fmt.get("size")
            if key_size is not None:
                return tuple(key_size)
        return tuple(fmt)

    def __init__(self):
        self.song_data = load_json(SONG_DB_PATH).get("songs", [])
        self.current_page = 0
        logging.info("Loaded song data: %s", json.dumps(self.song_data, indent=2))

    def render_button(self, deck, song):
        """Generate a button image for a song."""
        key_size = Controller.get_key_size(deck)
        icon_path = os.path.join(BASE_DIR, song.get("image", ""))
        try:
            icon = Image.open(icon_path)
        except FileNotFoundError:
            logging.warning("Image not found: %s, using default.", icon_path)
            icon = Image.new("RGB", key_size, (0, 0, 0))
        image = PILHelper.create_scaled_key_image(deck, icon)
        draw = ImageDraw.Draw(image)
        font_path = os.path.join(BASE_DIR, "assets", "DepartureMono-Regular.otf")
        font = ImageFont.truetype(font_path, 14)
        draw.text((image.width / 2, image.height - 10), song.get("title", ""),
                  font=font, anchor="ms", fill="white")
        return PILHelper.to_native_key_format(deck, image)

    def update_buttons(self, deck):
        """
        Update the buttons on the device as follows:
          - Main keys 0-6: Display song buttons (if available)
          - Main key 7: Displays the stop button
          - Touch keys 8 and 9: Set their color to indicate page navigation availability
        """
        key_size = Controller.get_key_size(deck)
        total_pages = (len(self.song_data) + Controller.SONGS_PER_PAGE - 1) // Controller.SONGS_PER_PAGE
        start_index = self.current_page * Controller.SONGS_PER_PAGE

        # Update main keys for songs (0-6)
        for key in range(Controller.SONGS_PER_PAGE):
            song_index = start_index + key
            if song_index < len(self.song_data):
                song = self.song_data[song_index]
                native_img = self.render_button(deck, song)
            else:
                placeholder = Image.new("RGB", key_size, (50, 50, 50))
                scaled = PILHelper.create_scaled_key_image(deck, placeholder)
                native_img = PILHelper.to_native_key_format(deck, scaled)
            deck.set_key_image(key, native_img)

        # Set stop button on main key 7
        stop_icon_path = os.path.join(BASE_DIR, "assets", "stop.png")
        try:
            stop_icon = Image.open(stop_icon_path)
        except FileNotFoundError:
            stop_icon = Image.new("RGB", key_size, (255, 0, 0))
        scaled = PILHelper.create_scaled_key_image(deck, stop_icon)
        native_img = PILHelper.to_native_key_format(deck, scaled)
        deck.set_key_image(Controller.STOP_BUTTON_INDEX, native_img)

        # Set navigation indicators on touch keys using set_key_color
        # Touch key 8: Previous page
        if self.current_page > 0:
            deck.set_key_color(Controller.NAV_BACK_INDEX, 255, 255, 255)  # White indicates available
        else:
            deck.set_key_color(Controller.NAV_BACK_INDEX, 0, 0, 0)    # Off

        # Touch key 9: Next page
        if self.current_page < total_pages - 1:
            deck.set_key_color(Controller.NAV_FORWARD_INDEX, 255, 255, 255)  # White indicates available
        else:
            deck.set_key_color(Controller.NAV_FORWARD_INDEX, 0, 0, 0)    # Off

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
                play_track(song.get("ableton_track"))
                self.update_buttons(deck)

# Singleton instance for callbacks
controller = Controller()

def update_buttons(deck):
    controller.update_buttons(deck)

def on_button_pressed(deck, key, state):
    controller.handle_button_press(deck, key, state)