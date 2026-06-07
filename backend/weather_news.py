import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_weather():
    try:
        lat = 17.3850
        lon = 78.4867
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=Asia/Kolkata"
        
        response = requests.get(url)
        data = response.json()
        
        current = data["current"]
        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        code = current["weather_code"]
        
        if code == 0:
            condition = "Clear sky ☀️"
        elif code in [1, 2, 3]:
            condition = "Partly cloudy ⛅"
        elif code in [45, 48]:
            condition = "Foggy 🌫️"
        elif code in [51, 53, 55]:
            condition = "Drizzling 🌦️"
        elif code in [61, 63, 65]:
            condition = "Rainy 🌧️"
        elif code in [80, 81, 82]:
            condition = "Rain showers 🌧️"
        elif code in [95, 96, 99]:
            condition = "Thunderstorm ⛈️"
        else:
            condition = "Cloudy ☁️"
        
        return f"""Weather in Hyderabad right now:
🌡️  Temperature: {temp}°C
💧 Humidity: {humidity}%
💨 Wind Speed: {wind} km/h
🌤️  Condition: {condition}"""
    
    except Exception as e:
        return "Sorry Krishna, I couldn't fetch the weather right now."

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