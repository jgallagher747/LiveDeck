import os
import sys
import time
from time import localtime, strftime
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

class InfoBar:
    def __init__(
        self,
        deck,
        total_pages=1,
        current_page=0,
        x_padding=15,
        boxes_right_margin=20,
        spacing=10,
        time_font_size=32,
        box_font_size=14
    ):
        """
        Initializes the InfoBar controller.
        
        Args:
            deck: The Stream Deck device.
            total_pages (int): Total number of pages.
            current_page (int): Current page index (0-indexed).
            x_padding (int): Left padding for the time text.
            boxes_right_margin (int): Right margin for the boxes.
            spacing (int): Spacing between boxes.
            time_font_size (int): Font size for the time display.
            box_font_size (int): Font size for the page boxes.
        """
        self.deck = deck
        self.total_pages = total_pages
        self.current_page = current_page
        self.x_padding = x_padding
        self.boxes_right_margin = boxes_right_margin
        self.spacing = spacing
        self.time_font_size = time_font_size
        self.box_font_size = box_font_size

        self.time_font = ImageFont.truetype(
            os.path.join(ASSETS_PATH, "DepartureMono-Regular.otf"), self.time_font_size
        )
        self.box_font = ImageFont.truetype(
            os.path.join(ASSETS_PATH, "DepartureMono-Regular.otf"), self.box_font_size
        )

    def clock(self):
        """Returns the current time as a formatted string."""
        return strftime("%I:%M", localtime())

    def get_page_info(self):
        """
        Determines the labels for the three page boxes.
        The center box always shows the current page (1-indexed),
        the left box shows the previous page (wrapping to the last page if at the start),
        and the right box shows the next page (wrapping to the first page if at the end).
        
        Returns:
            tuple: (boxes, dot_index)
                   boxes: a tuple of three strings representing the previous, current, and next page numbers.
                   dot_index: index (always 1) indicating the active (center) box.
        """
        if self.total_pages <= 1:
            boxes = ("1", "1", "1")
        else:
            current_display = self.current_page + 1
            left_page = self.total_pages if self.current_page == 0 else self.current_page
            right_page = 1 if self.current_page == self.total_pages - 1 else self.current_page + 2
            boxes = (str(left_page), str(current_display), str(right_page))
        return boxes, 1

    def render(self, time_str=None):
        """
        Renders the info bar image including the current time and page boxes.
        
        Args:
            time_str (str): Time string to display. If None, uses the current time.
        
        Returns:
            The image formatted for the Stream Deck screen.
        """
        if time_str is None:
            time_str = self.clock()

        image = PILHelper.create_screen_image(self.deck)
        draw = ImageDraw.Draw(image)

        # Fill the background
        draw.rectangle((0, 0, image.width, image.height), fill="black")

        # Draw the time text on the left
        time_bbox = draw.textbbox((0, 0), time_str, font=self.time_font)
        time_w = time_bbox[2] - time_bbox[0]
        time_h = time_bbox[3] - time_bbox[1]
        time_x = self.x_padding
        time_y = (image.height - time_h) // 4  # upper quarter of the screen
        draw.text((time_x, time_y), time_str, font=self.time_font, fill="white")

        # Get the page box labels and active index
        boxes, dot_index = self.get_page_info()
        box_count = len(boxes)
        box_width = 24
        box_height = 24
        total_boxes_width = box_count * (box_width + self.spacing) - self.spacing
        boxes_x_start = image.width - total_boxes_width - self.boxes_right_margin

        # Draw each page box
        for i, box_text in enumerate(boxes):
            x = boxes_x_start + i * (box_width + self.spacing)
            y = (image.height - box_height) // 2
            draw.rectangle([x, y, x + box_width, y + box_height], outline="white", width=1)

            box_bbox = draw.textbbox((0, 0), box_text, font=self.box_font)
            tw = box_bbox[2] - box_bbox[0]
            th = box_bbox[3] - box_bbox[1]
            text_x = x + (box_width - tw) / 2
            text_y = y + (box_height - th) / 2
            draw.text((text_x, text_y), box_text, font=self.box_font, fill="white")

                    # Draw a small colored dot below the active page box
        if 0 <= dot_index < box_count:
            dot_radius = 3
            dot_center_x = boxes_x_start + dot_index * (box_width + self.spacing) + (box_width // 2)
            dot_center_y = y + box_height + 6  # 6 pixels below the box
            draw.ellipse(
                [
                    (dot_center_x - dot_radius, dot_center_y - dot_radius),
                    (dot_center_x + dot_radius, dot_center_y + dot_radius)
                ],
                fill="blue"
            )

        # The center box (index 1) is always the active indicator; no moving dot needed.
        return PILHelper.to_native_screen_format(self.deck, image)

    def update(self, time_str=None):
        """
        Renders and updates the Stream Deck screen with the current info bar.
        """
        img = self.render(time_str)
        self.deck.set_screen_image(img)

    def set_page(self, current_page, total_pages=None):
        """
        Updates the current page (and optionally total pages) and refreshes the info bar.
        
        Args:
            current_page (int): New current page index (0-indexed).
            total_pages (int, optional): New total number of pages.
        """
        self.current_page = current_page
        if total_pages is not None:
            self.total_pages = total_pages
        self.update()

    def run_loop(self):
        """
        Runs an update loop that refreshes the info bar every second.
        This method blocks until interrupted.
        """
        last_update_time = 0
        try:
            while True:
                now = time.monotonic()
                if now - last_update_time >= 1:
                    self.update()
                    last_update_time = now
                time.sleep(0.016)  # ~60 FPS for responsiveness
        except KeyboardInterrupt:
            print("\nExiting InfoBar update loop...")
            self.deck.reset()
            self.deck.close()

if __name__ == "__main__":
    from StreamDeck.DeviceManager import DeviceManager

    streamdecks = DeviceManager().enumerate()
    if not streamdecks:
        print("No Stream Deck devices found.")
        sys.exit(1)

    deck = streamdecks[0]
    if deck.is_visual():
        deck.open()
        deck.reset()
        deck.set_brightness(50)

        # For testing: assume there are 5 pages and start at page 0
        info_bar = InfoBar(deck, total_pages=5, current_page=0)
        info_bar.run_loop()