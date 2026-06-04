import speech_recognition as sr
import edge_tts
import asyncio
import pygame
import os
import tempfile

VOICE = "hi-IN-SwaraNeural"

async def speak_async(text):
    try:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_path = tmp_file.name
        tmp_file.close()

        communicate = edge_tts.Communicate(text, VOICE, rate="+15%", pitch="+20Hz")
        await communicate.save(tmp_path)

        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        pygame.mixer.music.unload()
        os.unlink(tmp_path)

    except Exception as e:
        print(f"Voice error: {e}")

def speak(text):
    print(f"Mawa: {text}")
    try:
        asyncio.run(speak_async(text))
    except Exception as e:
        print(f"Speech error: {e}")

def detect_language(text):
    text_lower = text.lower().strip()

    # Hindi words list
    hindi_words = [
        "namaste", "namaskar", "kya", "hai", "mera", "tera",
        "aaj", "kal", "karo", "batao", "dikhao", "theek",
        "accha", "haan", "nahi", "mausam", "abhi", "bahut",
        "aur", "baje", "alvida", "suprabhat", "madad",
        "chahiye", "hain", "gaya", "mein", "yahan",
        "kaisa", "kaise", "kahan", "kitna", "subah",
        "shaam", "raat", "din", "hafte", "ghante", "sunao"
    ]

    words = text_lower.split()
    hindi_count = sum(1 for word in words if word in hindi_words)

    # Hindi Unicode characters
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')

    if hindi_count >= 2 or hindi_chars > 0:
        return "hindi"
    return "english"

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("🎤 Listening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("🔄 Processing...")

            # Step 1: Try English US first
            try:
                text = recognizer.recognize_google(audio, language="en-US")
                
                # Step 2: Check if result has Hindi script
                hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
                
                if hindi_chars > 0:
                    # Hindi script detected - it's Hindi
                    print(f"You said (Hindi): {text}")
                    return text.lower(), "hindi"
                else:
                    # No Hindi script - check words
                    lang = detect_language(text)
                    print(f"You said ({lang}): {text}")
                    return text.lower(), lang

            except Exception as e:
                print(f"English recognition failed: {e}")

            # Step 3: Fallback to Hindi
            try:
                text = recognizer.recognize_google(audio, language="hi-IN")
                print(f"You said (Hindi fallback): {text}")
                return text.lower(), "hindi"
            except:
                pass

            speak("Sorry Krishna, please try again!")
            return None, None

        except sr.WaitTimeoutError:
            return None, None

        except sr.UnknownValueError:
            speak("Sorry Krishna, samajh nahi aaya!")
            return None, None

        except sr.RequestError:
            speak("Voice service unavailable right now Krishna.")
            return None, None
