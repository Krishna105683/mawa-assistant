import requests

def search_jiosaavn(query):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        # iTunes API
        url = f"https://itunes.apple.com/search?term={query.replace(' ', '+')}&media=music&limit=5&country=IN"
        response = requests.get(url, timeout=15, headers=headers)
        
        if response.status_code == 200 and response.text:
            data = response.json()
            if data.get("results"):
                songs = data["results"]
                results = []
                for song in songs[:5]:
                    preview_url = song.get("previewUrl", "")
                    if preview_url:  # Only include songs with preview
                        results.append({
                            "id": str(song.get("trackId", "")),
                            "name": song.get("trackName", "Unknown"),
                            "artist": song.get("artistName", "Unknown"),
                            "image": song.get("artworkUrl100", "").replace("100x100", "300x300"),
                            "url": preview_url,
                            "duration": song.get("trackTimeMillis", 0) // 1000
                        })
                return results
        return []
    except Exception as e:
        print(f"Music search error: {e}")
        return []