import os
import struct
import wave
import pyaudio
import pvporcupine
import pvcobra
from dotenv import dotenv_values

# --- Configuration ---
config = dotenv_values(".env")
PICOVOICE_KEY = config.get("PicovoiceAccessKey")
MODEL_PATH = "hotword_model/hey_jarvis.ppn"

# --- Audio Recording and VAD ---
pa = None
audio_stream = None
porcupine = None
cobra = None

def listen_and_record() -> str | None:
    """
    A professional-grade listening loop that uses Porcupine for hotword
    and Cobra for Voice Activity Detection to record a clean command.
    """
    global pa, audio_stream, porcupine, cobra
    
    command_audio_path = "Data/command.wav"

    try:
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_KEY,
            keyword_paths=[MODEL_PATH], 
            sensitivities=[0.7]
        )
        
        # --- THIS IS THE CRITICAL FIX ---
        # The correct function is pvcobra.Cobra(), not .create()
        cobra = pvcobra.create(
            access_key=PICOVOICE_KEY
        )
        # --- END OF FIX ---
        
        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length)

        print("💤 Sleeping... (Listening for 'Jarvis')")
        
        # 1. Hotword Detection Loop
        while True:
            # Read audio as raw bytes
            pcm_bytes = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            # Unpack bytes into integers for processing
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm_bytes)
            
            if porcupine.process(pcm_unpacked) >= 0:
                print("✅ Hotword Detected! Now listening for command...")
                break

        # 2. VAD and Recording Loop
        frames = []
        # Add the last audio chunk to the buffer to catch commands spoken immediately
        frames.append(pcm_bytes)
        
        silence_frames = 0
        silence_threshold = int(cobra.sample_rate / porcupine.frame_length * 1.5) # 1.5s of silence

        while True:
            pcm_bytes = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            frames.append(pcm_bytes) # Append raw bytes for saving
            
            # Unpack for VAD processing
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm_bytes)
            
            voice_activity = cobra.process(pcm_unpacked)
            if voice_activity > 0.3:
                silence_frames = 0
            else:
                silence_frames += 1
            
            if silence_frames > silence_threshold:
                print("👂 Silence detected. Recording finished.")
                break

        # Ensure we have a meaningful amount of audio before saving
        min_frames = int(cobra.sample_rate * 0.5 / porcupine.frame_length)
        if len(frames) < min_frames:
            print("🎤 Command too short or empty. Ignoring.")
            return None

        # Save the recorded audio to a file
        with wave.open(command_audio_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
            wf.setframerate(porcupine.sample_rate)
            wf.writeframes(b''.join(frames))
        
        return command_audio_path

    except Exception as e:
        print(f"An error occurred in the audio loop: {e}")
        return None
    finally:
        # Cleanup all resources
        if audio_stream is not None: audio_stream.close()
        if pa is not None: pa.terminate()
        if cobra is not None: cobra.delete()
        if porcupine is not None: porcupine.delete()
