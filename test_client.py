import requests
import os

# The address of our running Jarvis server
SERVER_URL = "http://127.0.0.1:8000/api/jarvis"


# The path to the sample audio file we want to send
AUDIO_FILE_PATH = os.path.join("Data", "command.wav")

def run_test():
    """
    Sends a sample audio file to the Jarvis server and prints the response.
    """
    if not os.path.exists(AUDIO_FILE_PATH):
        print(f"❌ Error: Audio file not found at '{AUDIO_FILE_PATH}'")
        print("Please run the old 'core/main.py' once to generate a sample command.wav file.")
        return

    try:
        print(f"📡 Sending audio from '{AUDIO_FILE_PATH}' to the Jarvis server...")
        
        # Open the audio file in binary read mode
        with open(AUDIO_FILE_PATH, 'rb') as audio_file:
            # Prepare the file for the POST request
            files = {'audio': (os.path.basename(AUDIO_FILE_PATH), audio_file, 'audio/wav')}
            
            # Send the request
            response = requests.post(SERVER_URL, files=files)
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Print the JSON response from the server
            print("\n✅ Server Response Received:")
            print(response.json())

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error connecting to the server: {e}")
        print("Is your 'server.py' still running in the other terminal?")

if __name__ == "__main__":
    run_test()
