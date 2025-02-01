import os
import json

# Get the script's actual location (the PyLive project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Force the script to use the correct working directory
os.chdir(BASE_DIR)

print(f"DEBUG: Forced Working Directory to: {os.getcwd()}")

# Now build the absolute path to songs.json
SONG_DB_PATH = os.path.join(BASE_DIR, "config", "songs.json")

# Debugging: Print where we expect the file to be
print(f"DEBUG: Looking for songs.json at: {SONG_DB_PATH}")

# Verify the file exists before opening it
if not os.path.exists(SONG_DB_PATH):
    print(f"ERROR: File not found: {SONG_DB_PATH}")
else:
    with open(SONG_DB_PATH, "r") as file:
        data = json.load(file)
        print(json.dumps(data, indent=4))  # Pretty-print JSON to verify