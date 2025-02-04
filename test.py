import requests

import requests

def get_album_art(album_name):
    # Format the query for iTunes API
    base_url = "https://itunes.apple.com/search"
    params = {
        "term": album_name,
        "media": "music",
        "entity": "album",
        "limit": 1
    }

    # Make request to iTunes API
    response = requests.get(base_url, params=params)
    data = response.json()

    # Check if results exist
    if data["resultCount"] > 0:
        album = data["results"][0]
        artwork_url = album["artworkUrl100"].replace("100x100bb", "600x600bb")  # Get high-res version
        return artwork_url
    else:
        return None

# Example usage
album_name = "Abbey Road"
art_url = get_album_art(album_name)
if art_url:
    print(f"Album Art URL: {art_url}")
else:
    print("Album not found.")

import requests

def download_album_art(album_name, save_path="album_art.jpg"):
    art_url = get_album_art(album_name)
    
    if art_url:
        response = requests.get(art_url)
        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"Saved album art to {save_path}")
    else:
        print("Album art not found.")

# Example usage
download_album_art("Abbey Road", "abbey_road.jpg")