import os
import time
import asyncio
import pygame
import edge_tts
from dotenv import dotenv_values

# --- Configuration ---
# Loads your settings from the .env file.
config = dotenv_values(".env")
ENGLISH_VOICE = config.get("EnglishVoice", "en-CA-LiamNeural")
HINDI_VOICE = config.get("HindiVoice", "hi-IN-MadhurNeural")
AUDIO_FILE_PATH = "Data/speech.mp3"

# --- Initialization ---
# Initializes the Pygame audio mixer when the program starts.
pygame.mixer.init()

# --- Helper function to play audio ---
def _play_audio_sync():
    """
    This is a synchronous (blocking) function that handles playing the audio file.
    It's designed to be run in a separate thread so it doesn't freeze the assistant.
    """
    try:
        # Load the generated MP3 file into the music player.
        pygame.mixer.music.load(AUDIO_FILE_PATH)
        # Play the audio.
        pygame.mixer.music.play()
        # This loop waits until the music has completely finished playing.
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        # Crucially, unload the music to release the file lock.
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        # This 'finally' block ensures the audio file is ALWAYS deleted afterwards.
        if os.path.exists(AUDIO_FILE_PATH):
           try:
               # Added a tiny delay to ensure the OS has released the file lock.
               time.sleep(0.1)
               os.remove(AUDIO_FILE_PATH)
           except PermissionError as e:
               print(f"Could not remove audio file (it might be in use): {e}")

# --- Main Speak Function ---
async def speak(text: str):
    """
    This is the main asynchronous function for text-to-speech.
    It generates the audio file and then calls the playback function.
    """
    try:
        # Reads the language_state.txt file to decide which voice to use.
        try:
            with open("Data/language_state.txt", "r") as f:
                language = f.read().strip()
        except FileNotFoundError:
            language = "english" # Defaults to English if the file doesn't exist.

        voice_to_use = HINDI_VOICE if language == "hindi" else ENGLISH_VOICE
        
        # Generates the MP3 file from the text using edge-tts.
        communicate = edge_tts.Communicate(text, voice_to_use, pitch="+5Hz", rate="+13%")
        await communicate.save(AUDIO_FILE_PATH)
        
        # Runs the blocking _play_audio_sync function in a separate thread.
        # This is the correct way to handle blocking code in an async program.
        await asyncio.to_thread(_play_audio_sync)
    except Exception as e:
        print(f"An error occurred during text-to-speech: {e}")

