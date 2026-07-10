import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_weather(lat=None, lon=None, city=None):
    try:
        # Use user's location if provided, else default to Hyderabad
        if city and city != "Hyderabad":
            location = city
        elif lat and lon:
            location = f"{lat},{lon}"
        else:
            location = "Hyderabad"

        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(url, timeout=15, headers={"User-Agent": "curl/7.68.0"})
        data = response.json()

        current = data["current_condition"][0]
        temp = current["temp_C"]
        humidity = current["humidity"]
        wind = current["windspeedKmph"]
        desc = current["weatherDesc"][0]["value"]
        feels_like = current["FeelsLikeC"]

        # Get city name from response
        nearest_area = data.get("nearest_area", [{}])[0]
        area_name = nearest_area.get("areaName", [{}])[0].get("value", city or "Hyderabad")

        return f"Weather in {area_name} right now:\n🌡️  Temperature: {temp}°C (Feels like {feels_like}°C)\n💧 Humidity: {humidity}%\n💨 Wind Speed: {wind} km/h\n🌤️  Condition: {desc}"

    except Exception as e:
        try:
            location = city or "Hyderabad"
            url = f"https://wttr.in/{location}?format=3"
            response = requests.get(url, timeout=10, headers={"User-Agent": "curl/7.68.0"})
            return f"Weather in {location}: {response.text.strip()}"
        except:
            return "Weather service temporarily unavailable. Please try again later!"

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
                    news_text = "Here are today's top headlines:\n"
                    for i, entry in enumerate(feed.entries[:5], 1):
                        news_text += f"\n{i}. {entry.title}"
                    return news_text
            except:
                continue
        return "Sorry, couldn't fetch news right now!"
    except Exception as e:
        return f"News error: {str(e)}"