import requests

def search_jiosaavn(query):
    try:
        # JioSaavn unofficial API
        url = f"https://saavn.dev/api/search/songs?query={query}&page=1&limit=5"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("success") and data.get("data", {}).get("results"):
            songs = data["data"]["results"]
            results = []
            for song in songs[:5]:
                results.append({
                    "id": song.get("id"),
                    "name": song.get("name"),
                    "artist": song.get("artists", {}).get("primary", [{}])[0].get("name", "Unknown"),
                    "image": song.get("image", [{}])[-1].get("url", ""),
                    "url": song.get("downloadUrl", [{}])[-1].get("url", ""),
                    "duration": song.get("duration", 0)
                })
            return results
        return []
    except Exception as e:
        print(f"Music search error: {e}")
        return []

def get_song_url(song_id):
    try:
        url = f"https://saavn.dev/api/songs/{song_id}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("success") and data.get("data"):
            song = data["data"][0]
            download_urls = song.get("downloadUrl", [])
            # Get highest quality
            for quality in ["320kbps", "160kbps", "96kbps"]:
                for dl in download_urls:
                    if dl.get("quality") == quality:
                        return dl.get("url")
        return None
    except Exception as e:
        print(f"Song URL error: {e}")
        return None