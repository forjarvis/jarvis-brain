import speech_recognition as sr
import os

def transcribe_audio(file_path: str) -> str | None:
    """
    Transcribes the given audio file using Google's free STT API.
    """
    if not os.path.exists(file_path):
        return None
        
    r = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = r.record(source)
        
        print("🎙️ Transcribing audio...")
        text = r.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        print("⚠️ Google STT could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"⚠️ Could not request results from Google STT; {e}")
        return None
    finally:
        # Clean up the audio file
        if os.path.exists(file_path):
            os.remove(file_path)
