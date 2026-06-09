import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_weather():
    try:
        # Using wttr.in - works perfectly on all servers
        url = "https://wttr.in/Hyderabad?format=j1"
        response = requests.get(url, timeout=15, headers={"User-Agent": "curl/7.68.0"})
        data = response.json()
        
        current = data["current_condition"][0]
        temp = current["temp_C"]
        humidity = current["humidity"]
        wind = current["windspeedKmph"]
        desc = current["weatherDesc"][0]["value"]
        feels_like = current["FeelsLikeC"]
        
        return f"Weather in Hyderabad right now:\n🌡️  Temperature: {temp}°C (Feels like {feels_like}°C)\n💧 Humidity: {humidity}%\n💨 Wind Speed: {wind} km/h\n🌤️  Condition: {desc}"
    
    except Exception as e:
        try:
            # Fallback to simple format
            url = "https://wttr.in/Hyderabad?format=3"
            response = requests.get(url, timeout=10, headers={"User-Agent": "curl/7.68.0"})
            return f"Weather in Hyderabad: {response.text.strip()}"
        except:
            return "Weather in Hyderabad: Service temporarily unavailable. Please try again later!"
def get_news():
    try:
        import feedparser
        feeds = [
            "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
            "https://www.thehindu.com/feeder/default.rss",
            "https://indianexpress.com/feed/",
            "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
        ]
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                if feed.entries:
                    news_text = "Here are today's top headlines Krishna:\n"
                    for i, entry in enumerate(feed.entries[:5], 1):
                        news_text += f"\n{i}. {entry.title}"
                    return news_text
            except:
                continue
        return "Sorry Krishna, couldn't fetch news right now!"
    except Exception as e:
        return f"News error: {str(e)}"