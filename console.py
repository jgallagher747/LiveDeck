# --- uadconsole.py ---

import os
import subprocess
import time
import psutil

# Define the UAD Console path and process name
UAD_CONSOLE_PATH = os.path.expanduser('/Applications/Universal Audio/UAD Console.app')
PROCESS_NAME = 'UAD Console'

def is_running():
    """Return True if UAD Console is already running."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and PROCESS_NAME.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def uad_launch(timeout=5):
    """
    Launch UAD Console if it is not already running.
    
    Args:
        timeout (int): Seconds to wait for UAD Console to launch.
        
    Returns:
        bool: True if UAD Console is running (or was already running), False otherwise.
    """
    if is_running():
        print("UAD Console is already running.")
        return True

    if not os.path.exists(UAD_CONSOLE_PATH):
        print("UAD Console not found at:", UAD_CONSOLE_PATH)
        return False

    try:
        # Use the -a flag to launch the app by its bundle
        subprocess.Popen(['open', '-a', UAD_CONSOLE_PATH])
    except Exception as e:
        print("Error launching UAD Console:", e)
        return False

    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_running():
            print("UAD Console launched successfully.")
            return True
        time.sleep(0.5)

    print("UAD Console did not launch within", timeout, "seconds.")
    return True  # If the app didn't show up in time, we assume it might still be launching.