import os
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper
from config import FONT_PATH

def ensure_file_exists(filepath, default_content=""):
    """
    Ensures a file exists. If not, creates it with default content.

    Args:
        filepath (str): Path to the file.
        default_content (str, optional): Content to write if file does not exist.
    """
    if not os.path.exists(filepath):
        with open(filepath, "w") as file:
            file.write(default_content)
        print(f"Created missing file: {filepath}")

def render_button(deck, label, image_path):
    """
    Generates a button image with album art and a text label.

    Args:
        deck: Stream Deck device.
        label (str): Text to display on the button.
        image_path (str): Path to album art.

    Returns:
        Image: Formatted image for Stream Deck.
    """
    try:
        icon = Image.open(image_path)
    except FileNotFoundError:
        print(f"Warning: Image not found {image_path}, using default.")
        icon = Image.new("RGB", (deck.key_image_format()[0], deck.key_image_format()[1]), (0, 0, 0))

    image = PILHelper.create_scaled_key_image(deck, icon)

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, 14)

    draw.text((image.width / 2, image.height - 10), label, font=font, anchor="ms", fill="white")

    return PILHelper.to_native_key_format(deck, image)

def log(message):
    """
    Simple logging function.

    Args:
        message (str): Message to log.
    """
    print(f"[LOG] {message}")