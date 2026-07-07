import requests

def search_jiosaavn(query):
    try:
        # Try alternative JioSaavn API
        url = f"https://jiosaavn-api-privatecvc2.vercel.app/search/songs?query={query}&page=1&limit=5"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("data") and data["data"].get("results"):
            songs = data["data"]["results"]
            results = []
            for song in songs[:5]:
                # Get download URL
                download_urls = song.get("downloadUrl", [])
                audio_url = ""
                for dl in download_urls:
                    if dl.get("quality") in ["320kbps", "160kbps", "96kbps"]:
                        audio_url = dl.get("link", "")
                        break
                
                results.append({
                    "id": song.get("id", ""),
                    "name": song.get("name", "Unknown"),
                    "artist": song.get("primaryArtists", "Unknown"),
                    "image": song.get("image", [{}])[-1].get("link", "") if song.get("image") else "",
                    "url": audio_url,
                    "duration": song.get("duration", 0)
                })
            return results
        return []
    except Exception as e:
        print(f"Music search error: {e}")
        return []