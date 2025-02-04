# --- main.py ---
import time
import os
from streamdeck import initialize_streamdeck

# Get the script's actual location (the LiveDeck project root)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(BASE_DIR)

# Update any direct artwork path references
ARTWORK_PATH = "assets/artwork"  # Update from "artwork" if it exists

def init():
    os.makedirs(ARTWORK_PATH, exist_ok=True)
    # ... rest of initialization ...

def main():
    """
    Main function that initializes the Stream Deck and listens for events.
    """
    deck = initialize_streamdeck()
    if not deck:
        print("Stream Deck initialization failed. Exiting.")
        return
    
    print("Stream Deck initialized. Listening for button events...")
    try:
        while True:
            time.sleep(1)  # Keep script running efficiently
    except KeyboardInterrupt:
        print("\nShutting down Stream Deck...")
        deck.reset()
        deck.close()


if __name__ == "__main__":
    main()