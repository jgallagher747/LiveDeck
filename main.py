from streamdeck import initialize_streamdeck
import time
import os

# Get the script's actual location (the PyLive project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Force the script to use the correct working directory
os.chdir(BASE_DIR)

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