# --- screen.py ---

import os
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

# Generate an image for the screen
def render_screen_image(deck, font_filename, text):
    image = PILHelper.create_screen_image(deck)
    # Load a custom TrueType font and use it to create an image
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 20)
    draw.text((image.width / 2, image.height - 25), text=text, font=font, anchor="ms", fill="white")

    return PILHelper.to_native_screen_format(deck, image)


if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        # This example only works with devices that have screens.
        if not deck.is_visual():
            continue

        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}', fw: '{}')".format(
            deck.deck_type(), deck.get_serial_number(), deck.get_firmware_version()
        ))

        # Set initial screen brightness to 30%.
        deck.set_brightness(30)

                # Set a screen image
        image = render_screen_image(deck, os.path.join(ASSETS_PATH, "DepartureMono-Regular.otf"), "Python StreamDeck")
        deck.set_screen_image(image)


# def create_page_status_icon(current_page, total_pages, width=150, height=50):
#     """
#     Generates a page status icon image.

#     :param current_page: Current page number (1-based index)
#     :param total_pages: Total number of pages
#     :param width: Image width
#     :param height: Image height
#     :return: PIL Image object
#     """

#     # Create image canvas with transparent background
#     img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
#     draw = ImageDraw.Draw(img)

#     # Define box sizes and positions
#     box_width = 30
#     box_height = 30
#     box_spacing = 10
#     x_offset = width - (box_width * 3 + box_spacing * 2)  # Right-align

#     # Colors
#     white = (255, 255, 255, 255)
#     grey = (128, 128, 128, 255)
#     blue = (0, 0, 255, 255)

#     # Determine left and right page numbers
#     left_page = total_pages if current_page == 1 else current_page - 1
#     right_page = 1 if current_page == total_pages else current_page + 1

#     # Draw left box (previous page or last page)
#     draw.rectangle([x_offset, (height - box_height) // 2, x_offset + box_width, (height + box_height) // 2], fill=grey)
    
#     # Draw center box (current page)
#     draw.rectangle(
#         [x_offset + box_width + box_spacing, (height - box_height) // 2,
#          x_offset + (box_width * 2) + box_spacing, (height + box_height) // 2],
#         fill=white
#     )

#     # Draw right box (next page or first page)
#     draw.rectangle(
#         [x_offset + (box_width * 2) + (box_spacing * 2), (height - box_height) // 2,
#          x_offset + (box_width * 3) + (box_spacing * 2), (height + box_height) // 2],
#         fill=grey
#     )

#     # Draw blue dot below center box
#     dot_radius = 5
#     draw.ellipse(
#         [x_offset + box_width + box_spacing + (box_width // 2) - dot_radius,
#          height - 10 - dot_radius,
#          x_offset + box_width + box_spacing + (box_width // 2) + dot_radius,
#          height - 10 + dot_radius],
#         fill=blue
#     )

#     # Load font (use default system font)
#     try:
#         font = ImageFont.truetype("arial.ttf", 14)
#     except IOError:
#         font = ImageFont.load_default()

#     # Draw page numbers
#     draw.text((x_offset + 10, (height - box_height) // 2 + 8), str(left_page), fill="black", font=font)
#     draw.text((x_offset + box_width + box_spacing + 10, (height - box_height) // 2 + 8), str(current_page), fill="black", font=font)
#     draw.text((x_offset + (box_width * 2) + (box_spacing * 2) + 10, (height - box_height) // 2 + 8), str(right_page), fill="black", font=font)

#     return img

# # Example Usage
# icon = create_page_status_icon(1, 5)
# icon.show()  # Opens image preview
# icon.save("page_status.jpg")  # Saves as a PNG file



  