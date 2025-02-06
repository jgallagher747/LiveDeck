# --- ableton.py ---
import logging
from live import Set
from pythonosc import udp_client
import os
import subprocess
import time
import psutil

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class AbletonConnection:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.is_connected = False
            self.ableton_set = None
            self.osc_client = None
            self.initialize_osc()
    
    def initialize_osc(self):
        """Initialize OSC client"""
        OSC_IP = "127.0.0.1"
        OSC_PORT = 8000
        self.osc_client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)
        logging.info("OSC client initialized")
    
    def is_ableton_running(self):
        """Check if Ableton Live is already running"""
        return any('Ableton Live' in p.name() for p in psutil.process_iter(['name']))
    
    def launch_set(self, set_path):
        """
        Launch Ableton Live with a specific set file.
        
        Args:
            set_path (str): Full path to the .als file
        """
        # If we're already connected, don't try again
        if self.is_connected:
            logging.info("Already connected to Ableton Live")
            return True
        
        logging.info("Checking Ableton Live status...")
        
        # Check if Ableton is already running
        if self.is_ableton_running():
            self.is_connected = True
            logging.info("Ableton Live is already running")
            return True
        
        # Ensure the path exists
        if not os.path.exists(set_path):
            logging.error(f"Ableton Live set not found: {set_path}")
            return False
            
        try:
            logging.info("Launching Ableton Live...")
            subprocess.Popen(['open', set_path])
            
            # Quick check for first 3 seconds
            for _ in range(5):
                if self.is_ableton_running():
                    self.is_connected = True
                    logging.info("Ableton Live launched successfully")
                    return True
                time.sleep(1)
                
            logging.warning("Ableton Live launch taking longer than expected, continuing anyway")
            self.is_connected = True
            return True
            
        except Exception as e:
            logging.error(f"Error launching Ableton Live: {e}")
            return False
    
    def connect_to_set(self):
        """Initialize connection to Ableton Live set"""
        try:
            self.ableton_set = Set(scan=True)
            logging.info("Connected to Ableton Live set")
            return True
        except Exception as e:
            logging.error(f"Error connecting to Ableton Live set: {e}")
            return False
    
    def send_reset_osc(self):
        """Sends an OSC message to reset the playhead."""
        if self.osc_client:
            self.osc_client.send_message("/reset", 0)
            logging.info("Sent OSC reset command to Max for Live.")
    
    def play_track(self, track_index):
        """Plays a specific track in Ableton."""
        if not self.ableton_set:
            if not self.connect_to_set():
                return
        
        self.send_reset_osc()
        
        try:
            track = self.ableton_set.tracks[track_index]
        except IndexError:
            logging.error(f"Invalid track index: {track_index}")
            return
        
        for t in self.ableton_set.tracks:
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
    
    def stop_all(self):
        """Stops all playback in Ableton Live via OSC."""
        if self.osc_client:
            self.osc_client.send_message("/stop", 0)
            logging.info("Sent OSC stop command to Max for Live.")

        if self.ableton_set:
            for track in self.ableton_set.tracks:
                if not track.clips:
                    continue
                for clip in track.clips:
                    if clip:
                        try:
                            clip.stop()
                        except Exception as e:
                            logging.error(f"Error stopping clip on '{track.name}': {e}")
            logging.info("All playback stopped.")

# Add the set path as a constant
ABLETON_SET_PATH = '/Users/deepthought-mini/Documents/Live Sets/Backing Tracks Project/Backing Tracks.als'

# Create global instance
ableton = AbletonConnection()

# Convenience functions that use the singleton
def launch_ableton_set(set_path):
    return ableton.launch_set(set_path)

def play_track(track_index):
    return ableton.play_track(track_index)

def stop_all():
    return ableton.stop_all()

def send_reset_osc():
    return ableton.send_reset_osc()

class AbletonInterface:
    def __init__(self):
        self.artwork_path = "assets/artwork"  # Update from "artwork" if it exists
        
    def get_track_artwork(self, track_name):
        # If there's any artwork handling, update the paths
        artwork_file = os.path.join(self.artwork_path, f"{track_name}.png")