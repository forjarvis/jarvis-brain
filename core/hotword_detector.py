import os
import struct
import pyaudio
import pvporcupine
from dotenv import dotenv_values

config = dotenv_values(".env")
PICOVOICE_KEY = config.get("PicovoiceAccessKey")

# --- MODIFIED: Path to your single keyword file ---
MODEL_PATH = "hotword_model/hey_jarvis.ppn" 

def listen_for_hotword():
    """
    Listens for the 'Hey Jarvis' hotword with adjusted sensitivity.
    """
    if not PICOVOICE_KEY:
        print("❌ Picovoice Access Key not found in .env file.")
        return False
    
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Hotword model file not found at {MODEL_PATH}")
        return False

    porcupine = None
    pa = None
    audio_stream = None

    try:
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_KEY,
            keyword_paths=[MODEL_PATH],
            # --- THE KEY FIX: Increased sensitivity ---
            # Default is 0.5. Let's try 0.7 to be more forgiving.
            sensitivities=[0.7] 
        )
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            result = porcupine.process(pcm)
            if result >= 0:
                print("✅ Hotword Detected!")
                return True

    except Exception as e:
        print(f"An error occurred with the hotword detector: {e}")
        return False
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()
