import requests

def search_jiosaavn(query):
    try:
        # iTunes API - free, no key needed, works everywhere
        url = f"https://itunes.apple.com/search?term={query}&media=music&limit=5&country=IN"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("results"):
            songs = data["results"]
            results = []
            for song in songs[:5]:
                results.append({
                    "id": str(song.get("trackId", "")),
                    "name": song.get("trackName", "Unknown"),
                    "artist": song.get("artistName", "Unknown"),
                    "image": song.get("artworkUrl100", ""),
                    "url": song.get("previewUrl", ""),
                    "duration": song.get("trackTimeMillis", 0) // 1000
                })
            return results
        return []
    except Exception as e:
        print(f"Music search error: {e}")
        return []