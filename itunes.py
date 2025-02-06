# import json
# import os
# import requests
# import time
# import logging
# from live import Set, Track
# from urllib.parse import quote

# class iTunesHelper:
#     def __init__(self, base_dir=".", log_level=logging.INFO):
#         """Initialize with more verbose logging setup"""
#         # Setup logging with more detailed format
#         self.logger = logging.getLogger(__name__)
#         self.logger.setLevel(log_level)
        
#         # Clear any existing handlers
#         self.logger.handlers = []
        
#         # Add console handler with detailed formatting
#         console_handler = logging.StreamHandler()
#         formatter = logging.Formatter(
#             '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
#         )
#         console_handler.setFormatter(formatter)
#         self.logger.addHandler(console_handler)

#         # Add file handler for persistent logging
#         log_file = os.path.join(base_dir, 'itunes_helper.log')
#         file_handler = logging.FileHandler(log_file)
#         file_handler.setFormatter(formatter)
#         self.logger.addHandler(file_handler)

#         self.logger.info("=== Starting new iTunesHelper session ===")
#         self.logger.info(f"Base directory: {base_dir}")
#         self.logger.info(f"Log file: {log_file}")

#         # Update paths to use assets/artwork
#         self.base_dir = base_dir
#         self.songs_json_path = os.path.join(base_dir, "songs.json")
#         self.assets_dir = os.path.join(base_dir, "assets")
#         self.image_asset_dir = os.path.join(self.assets_dir, "artwork")
#         self.logger.info(f"Initialized iTunesHelper with artwork path: {self.image_asset_dir}")

#         # Ensure both assets and artwork directories exist
#         os.makedirs(self.assets_dir, exist_ok=True)
#         os.makedirs(self.image_asset_dir, exist_ok=True)
#         self.logger.info(f"Initialized iTunesHelper with artwork path: {self.image_asset_dir}")

#         # Ableton connection
#         self.set_obj = None
#         self.track_names = []

#         # iTunes API configuration
#         self.itunes_search_url = "https://itunes.apple.com/search"
#         self.request_delay = 0.5
#         self.last_request_time = 0
        
#         self.logger.info("iTunesHelper initialization complete")

#         # Update any incorrect artwork paths
#         self.update_artwork_paths()

#     def connect_to_ableton(self):
#         """Establish connection to Ableton Live."""
#         self.logger.info("Attempting to connect to Ableton Live...")
#         try:
#             self.set_obj = Set(scan=True)  # Added scan=True parameter
#             self.logger.info("Successfully connected to Ableton Live")
#             return True
#         except Exception as e:
#             self.logger.error(f"Failed to connect to Ableton Live: {str(e)}")
#             self.logger.error(f"Exception type: {type(e).__name__}")
#             return False

#     def get_track_names_from_ableton(self):
#         """Get track names from currently open Ableton Live set."""
#         self.logger.info("Starting track name retrieval from Ableton")
        
#         try:
#             # Create fresh connection and get all track names in one go
#             self.set_obj = Set(scan=True)
#             self.track_names = [track.name for track in self.set_obj.tracks if track.name and track.name.strip()]
            
#             # Log results
#             self.logger.info(f"Total tracks in Ableton: {len(self.set_obj.tracks)}")
#             self.logger.info(f"Found {len(self.track_names)} named tracks")
            
#             if self.track_names:
#                 self.logger.info(f"Track names: {self.track_names}")
#             else:
#                 self.logger.warning("No named tracks found")
                
#             return self.track_names
            
#         except Exception as e:
#             self.logger.error(f"Error getting track names: {str(e)}")
#             self.logger.error(f"Exception type: {type(e).__name__}")
#             return []

#         finally:
#             # Clean up connection
#             if self.set_obj:
#                 try:
#                     self.set_obj._clean_up()
#                 except:
#                     pass

#     def process_ableton_tracks(self):
#         """Main method to process tracks from Ableton Live."""
#         track_names = self.get_track_names_from_ableton()
#         if not track_names:
#             self.logger.warning("No track names found in Ableton Live set")
#             return False
        
#         return self.process_tracks(track_names)

#     def load_songs_json(self):
#         """Load or initialize songs.json."""
#         if os.path.exists(self.songs_json_path):
#             self.logger.debug(f"Loading existing songs from {self.songs_json_path}")
#             with open(self.songs_json_path, "r") as f:
#                 return json.load(f)
#         self.logger.info(f"No existing songs.json found, initializing new one")
#         return {"songs": []}

#     def save_songs_json(self, data):
#         """Save updated songs.json."""
#         self.logger.debug(f"Saving songs data to {self.songs_json_path}")
#         with open(self.songs_json_path, "w") as f:
#             json.dump(data, f, indent=4)

#     def search_itunes(self, track_name, artist_name=None):
#         """Enhanced logging for iTunes search"""
#         self.logger.info(f"Starting iTunes search for: {track_name}")
        
#         # Rate limiting check
#         time_since_last_request = time.time() - self.last_request_time
#         if time_since_last_request < self.request_delay:
#             wait_time = self.request_delay - time_since_last_request
#             self.logger.info(f"Rate limiting: waiting {wait_time:.2f} seconds")
#             time.sleep(wait_time)

#         search_term = f"{artist_name} {track_name}" if artist_name else track_name
#         params = {
#             "term": quote(search_term),
#             "media": "music",
#             "entity": "song",
#             "limit": 1
#         }
        
#         self.logger.info(f"Search URL params: {params}")
        
#         try:
#             self.logger.debug("Making iTunes API request...")
#             response = requests.get(self.itunes_search_url, params=params)
#             self.last_request_time = time.time()
            
#             self.logger.info(f"iTunes API response status: {response.status_code}")
#             self.logger.debug(f"Response content: {response.text[:200]}...")  # First 200 chars

#             if response.status_code == 429:
#                 self.logger.warning("Rate limit hit, waiting before retry")
#                 time.sleep(5)  # Wait longer on rate limit
#                 return None

#             if response.status_code != 200:
#                 self.logger.error(f"iTunes API error: {response.status_code}")
#                 return None

#             data = response.json()
#             if not data.get("results"):
#                 self.logger.warning(f"No results found for: {search_term}")
#                 return None

#             result = data["results"][0]
#             return {
#                 "title": result.get("trackName", track_name),
#                 "album": result.get("collectionName", "Unknown Album"),
#                 "artist": result.get("artistName", "Unknown Artist"),
#                 "artwork_url": result.get("artworkUrl100", "").replace("100x100bb", "600x600bb")
#             }

#         except requests.exceptions.RequestException as e:
#             self.logger.error(f"Network error during iTunes search: {str(e)}")
#             return None
#         except json.JSONDecodeError as e:
#             self.logger.error(f"Error parsing iTunes response: {str(e)}")
#             return None

#     def download_artwork(self, track_name, artwork_url):
#         """
#         Download and save artwork as PNG file.
#         Returns relative path to saved file or None on failure.
#         """
#         if not artwork_url:
#             self.logger.warning(f"No artwork URL provided for: {track_name}")
#             return None

#         # Create safe filename
#         safe_name = "".join(c for c in track_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
#         safe_name = safe_name.lower().replace(' ', '_')
#         filename = f"{safe_name}.png"
#         filepath = os.path.join(self.image_asset_dir, filename)

#         try:
#             self.logger.debug(f"Downloading artwork for: {track_name}")
#             response = requests.get(artwork_url, stream=True)
#             response.raise_for_status()

#             with open(filepath, 'wb') as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     f.write(chunk)

#             relative_path = os.path.join("artwork", filename)
#             self.logger.info(f"Saved artwork to: {relative_path}")
#             return relative_path

#         except requests.exceptions.RequestException as e:
#             self.logger.error(f"Error downloading artwork for {track_name}: {str(e)}")
#             return None
#         except IOError as e:
#             self.logger.error(f"Error saving artwork for {track_name}: {str(e)}")
#             return None

#     def process_tracks(self, track_names):
#         """Process track list and update songs.json with metadata and artwork."""
#         if not track_names:
#             self.logger.warning("No tracks to process")
#             return False

#         # Load existing data
#         try:
#             with open(self.songs_json_path, 'r') as f:
#                 songs_data = json.load(f)
#         except (FileNotFoundError, json.JSONDecodeError):
#             songs_data = {"songs": []}

#         # Track existing entries
#         existing_titles = {song["title"] for song in songs_data["songs"]}
#         next_id = max((song["id"] for song in songs_data["songs"]), default=0) + 1

#         # Process each track
#         for index, track_name in enumerate(track_names):
#             if track_name in existing_titles:
#                 self.logger.info(f"Skipping existing track: {track_name}")
#                 continue

#             self.logger.info(f"Processing track {index + 1}/{len(track_names)}: {track_name}")
            
#             # Get metadata from iTunes
#             metadata = self.search_itunes(track_name)
#             if not metadata:
#                 continue

#             # Download artwork
#             artwork_path = self.download_artwork(track_name, metadata["artwork_url"])
#             if not artwork_path:
#                 artwork_path = "artwork/default.png"  # Fallback to default image

#             # Add to songs data
#             songs_data["songs"].append({
#                 "id": next_id,
#                 "title": track_name,
#                 "album": metadata["album"],
#                 "artist": metadata["artist"],
#                 "image": artwork_path,
#                 "ableton_track": index
#             })
#             next_id += 1

#         # Save updated data
#         try:
#             with open(self.songs_json_path, 'w') as f:
#                 json.dump(songs_data, f, indent=2)
#             self.logger.info("Successfully updated songs.json")
#             return True
#         except IOError as e:
#             self.logger.error(f"Error saving songs.json: {str(e)}")
#             return False

#     def get_album_art(self, album_name, artist_name=None):
#         """Get album artwork URL from iTunes."""
#         self.logger.info(f"Searching iTunes for album: {album_name}")
        
#         # Format the query for iTunes API
#         search_term = f"{artist_name} {album_name}" if artist_name else album_name
#         params = {
#             "term": search_term,
#             "media": "music",
#             "entity": "album",
#             "limit": 1
#         }

#         try:
#             response = requests.get(self.itunes_search_url, params=params)
#             data = response.json()

#             if data["resultCount"] > 0:
#                 album = data["results"][0]
#                 artwork_url = album["artworkUrl100"].replace("100x100bb", "600x600bb")
#                 self.logger.info(f"Found artwork for: {album_name}")
#                 return artwork_url
#             else:
#                 self.logger.warning(f"No artwork found for: {album_name}")
#                 return None
            
#         except Exception as e:
#             self.logger.error(f"Error fetching artwork for {album_name}: {str(e)}")
#             return None

#     def process_songs_json(self):
#         """Process existing songs.json and update with artwork."""
#         self.logger.info("Starting to process songs.json")
        
#         try:
#             # Load existing songs.json
#             if not os.path.exists(self.songs_json_path):
#                 self.logger.error("songs.json not found")
#                 return False
            
#             with open(self.songs_json_path, 'r') as f:
#                 songs_data = json.load(f)
            
#             if not songs_data.get("songs"):
#                 self.logger.error("No songs found in songs.json")
#                 return False
            
#             # Process each song
#             for song in songs_data["songs"]:
#                 self.logger.info(f"Processing song: {song['title']}")
                
#                 # Check if artwork exists in assets/artwork
#                 if song.get("image") and "assets/artwork" in song["image"]:
#                     self.logger.info(f"Artwork already exists for: {song['title']}")
#                     continue
                
#                 # Get artwork URL
#                 artwork_url = self.get_album_art(
#                     album_name=song.get("album", song["title"]),
#                     artist_name=song.get("artist")
#                 )
                
#                 if artwork_url:
#                     # Download and save artwork
#                     safe_name = "".join(c for c in song["title"] if c.isalnum() or c in (' ', '-', '_')).rstrip()
#                     safe_name = safe_name.lower().replace(' ', '_')
#                     artwork_path = os.path.join("assets/artwork", f"{safe_name}.png")
                    
#                     # Download artwork
#                     try:
#                         response = requests.get(artwork_url, stream=True)
#                         response.raise_for_status()
                        
#                         # Ensure the assets/artwork directory exists
#                         os.makedirs("assets/artwork", exist_ok=True)
                        
#                         with open(artwork_path, 'wb') as f:
#                             for chunk in response.iter_content(chunk_size=8192):
#                                 f.write(chunk)
                            
#                         # Update song data with path in assets/artwork
#                         song["image"] = artwork_path
#                         self.logger.info(f"Saved artwork for: {song['title']}")
                        
#                     except Exception as e:
#                         self.logger.error(f"Error saving artwork for {song['title']}: {str(e)}")
#                         song["image"] = "assets/artwork/default.png"
#                 else:
#                     song["image"] = "assets/artwork/default.png"
                
#                 # Rate limiting
#                 time.sleep(1)
            
#             # Save updated songs.json
#             with open(self.songs_json_path, 'w') as f:
#                 json.dump(songs_data, f, indent=2)
            
#             self.logger.info("Successfully updated songs.json with artwork")
#             return True
            
#         except Exception as e:
#             self.logger.error(f"Error processing songs.json: {str(e)}")
#             return False

#     def update_artwork_paths(self):
#         """Update artwork paths in songs.json to use correct assets/artwork directory"""
#         self.logger.info("Updating artwork paths in songs.json...")
        
#         try:
#             with open(self.songs_json_path, 'r') as f:
#                 songs_data = json.load(f)
            
#             updated = False
#             for song in songs_data.get("songs", []):
#                 if "image" in song:
#                     current_path = song["image"]
#                     filename = os.path.basename(current_path)
                    
#                     # Create the correct path relative to the project root
#                     new_path = os.path.join("assets", "artwork", filename)
                    
#                     # Only update if path is different
#                     if current_path != new_path:
#                         song["image"] = new_path
#                         updated = True
#                         self.logger.info(f"Updated path for {song['title']}: {current_path} -> {new_path}")
                        
#                         # Check if file exists in old location and move it
#                         old_full_path = os.path.join(self.base_dir, current_path)
#                         new_full_path = os.path.join(self.base_dir, new_path)
#                         if os.path.exists(old_full_path) and old_full_path != new_full_path:
#                             os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
#                             try:
#                                 os.rename(old_full_path, new_full_path)
#                                 self.logger.info(f"Moved file from {old_full_path} to {new_full_path}")
#                             except OSError as e:
#                                 self.logger.error(f"Error moving file: {e}")
            
#             if updated:
#                 with open(self.songs_json_path, 'w') as f:
#                     json.dump(songs_data, f, indent=2)
#                 self.logger.info("Successfully updated artwork paths in songs.json")
            
#         except Exception as e:
#             self.logger.error(f"Error updating artwork paths: {str(e)}")