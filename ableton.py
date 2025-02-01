# --- ableton.py ---
from live import Set
from pythonosc import udp_client

# Initialize Ableton Live connection
ableton_set = Set(scan=True)  # Scan the current Ableton project

# Configure OSC client to send commands to the Max for Live OSC monitor device.
# The Max for Live OSC monitor is now on a return track.
OSC_IP = "127.0.0.1"  # Typically localhost
OSC_PORT = 8000       # Use the port that your Max for Live OSC monitor is listening on

osc_client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)

def send_reset_osc():
    """
    Sends an OSC message to the Max for Live OSC monitor device to reset the playhead.
    """
    osc_client.send_message("/reset", 0)
    print("Sent OSC reset command to Max for Live.")


def play_track(track_index):
    """
    Plays a specific track in Ableton by first sending an OSC command
    to reset the playhead, then unsoloing all tracks, soloing the selected track,
    and starting playback.
    """
    send_reset_osc()  # Reset the playhead via OSC command

    # Un-solo all tracks first.
    for track in ableton_set.tracks:
        track.solo = False  

    if 0 <= track_index < len(ableton_set.tracks):
        track = ableton_set.tracks[track_index]
        track.solo = True  # Solo the selected track

        if track.clips and len(track.clips) > 0:
            clip = track.clips[0]
            if clip is not None:
                try:
                    clip.play()  # Play the first clip of the track.
                    print(f"Playing: {track.name}")
                except Exception as e:
                    print(f"Error playing clip on track '{track.name}': {e}")
            else:
                print(f"Track '{track.name}' has an invalid clip (None).")
        else:
            print(f"Track '{track.name}' has no clips to play.")
    else:
        print(f"Invalid track index: {track_index}")

def stop_all():
    """
    Stops all playback in Ableton Live by iterating over each track and clip.
    """
    for track in ableton_set.tracks:
        if track.clips:
            none_encountered = False
            for clip in track.clips:
                if clip is None:
                    none_encountered = True
                    continue
                try:
                    clip.stop()
                except Exception as e:
                    print(f"Error stopping clip on track '{track.name}': {e}")
            if none_encountered:
                print(f"Warning: Some clips on track '{track.name}' were invalid and skipped.")
    print("All playback stopped.")