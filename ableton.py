# --- ableton.py ---
import logging
from live import Set
from pythonosc import udp_client
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Initialize Ableton Live connection
ableton_set = Set(scan=True)

# Configure OSC client
OSC_IP = "127.0.0.1"
OSC_PORT = 8000
osc_client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)


def send_reset_osc():
    """Sends an OSC message to reset the playhead."""
    osc_client.send_message("/reset", 0)
    logging.info("Sent OSC reset command to Max for Live.")


def play_track(track_index):
    """Plays a specific track in Ableton."""
    send_reset_osc()
    
    try:
        track = ableton_set.tracks[track_index]
    except IndexError:
        logging.error(f"Invalid track index: {track_index}")
        return
    
    for t in ableton_set.tracks:
        if t.solo:
            t.solo = False
    
    track.solo = True
    
    if track.clips:
        clip = track.clips[0]
        if clip:
            try:
                clip.play()
                logging.info(f"Playing: {track.name}")
            except Exception as e:
                logging.error(f"Error playing clip on '{track.name}': {e}")


def stop_all():
    """Stops all playback in Ableton Live via OSC."""
    osc_client.send_message("/stop", 0)  # Ensure this is still included
    logging.info("Sent OSC stop command to Max for Live.")

    for track in ableton_set.tracks:
        if not track.clips:
            continue  # Skip tracks with no clips
        for clip in track.clips:
            if clip:
                try:
                    clip.stop()
                except Exception as e:
                    logging.error(f"Error stopping clip on '{track.name}': {e}")
    logging.info("All playback stopped.")


class AbletonInterface:
    def __init__(self):
        self.artwork_path = "assets/artwork"  # Update from "artwork" if it exists
        
    def get_track_artwork(self, track_name):
        # If there's any artwork handling, update the paths
        artwork_file = os.path.join(self.artwork_path, f"{track_name}.png")
        # ... rest of the method ...

    # ... rest of the class ...
