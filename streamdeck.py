# --- streamdeck.py ---
import os
import json
import logging
import psutil
import time
import platform
import subprocess
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from config import SONG_DB_PATH, load_json

logging.basicConfig(level=logging.INFO)

SONG_DATA = load_json(SONG_DB_PATH, {"songs": []})


def close_streamdeck_app():
    """Close the StreamDeck application if it's running"""
    streamdeck_processes = [
        'Stream Deck',
        'crashpad_handler',
        'termination_handler',
        'QtWebEngineProcess',
        'node20',
        'se.trevligaspel.midi'
    ]
    terminated = False

    logging.info("Starting StreamDeck app termination...")
    
    # First attempt to kill all StreamDeck-related processes
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            proc_name = str(proc.info['name']).strip()
            proc_exe = str(proc.info.get('exe', '')).strip()
            
            # Check if it's a StreamDeck-related process
            if any(name in proc_name for name in streamdeck_processes) or \
               'Elgato Stream Deck.app' in proc_exe:
                logging.info(f"Terminating: {proc_name} (PID: {proc.pid})")
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except psutil.TimeoutExpired:
                    logging.info(f"Force killing: {proc_name}")
                    proc.kill()  # Force kill if terminate doesn't work
                terminated = True
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"Error with process {proc_name}: {e}")
            continue

    if not terminated:
        logging.warning("No StreamDeck processes found to terminate")
    else:
        # Give extra time for all processes to fully terminate
        time.sleep(2)
        
    # Double check no StreamDeck processes are left
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if 'Stream Deck' in proc.info['name'] or 'Elgato Stream Deck.app' in str(proc.info.get('exe', '')):
                logging.warning(f"StreamDeck process still running: {proc.info['name']} (PID: {proc.pid})")
                proc.kill()  # Force kill any remaining processes
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Final wait to ensure everything is closed
    time.sleep(1)


def initialize_streamdeck():
    """Initialize StreamDeck by closing any running instance and starting a new one."""
    logging.info("Starting StreamDeck initialization...")
    
    # Close StreamDeck app
    close_streamdeck_app()

    # Initialize device
    manager = DeviceManager()
    streamdecks = manager.enumerate()
    if not streamdecks:
        logging.warning("No Stream Deck devices found.")
        return None

    deck = streamdecks[0]
    deck.open()
    logging.info(f"Connected to Stream Deck: {deck.deck_type()}")
    # Remove the call to update_buttons here.
    # The main program should call controller.update_buttons(deck)
    logging.info("Stream Deck initialized successfully")
    return deck


if __name__ == "__main__":
    deck = initialize_streamdeck()
    if deck:
        logging.info("Listening for Stream Deck events...")
        while True:
            pass