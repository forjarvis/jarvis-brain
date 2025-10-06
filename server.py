import asyncio
import json
import shutil
from fastapi import FastAPI, UploadFile, File

# Import all our Jarvis components
from utils.stt_processor import transcribe_audio
from brain.orchestrator import get_ai_response
from device_control.command_executor import execute_tool_call
from core.audio_manager_tts_only import speak
from utils.app_manager import sync_app_list

# Create the FastAPI app
app = FastAPI()

# --- The Main Agentic Loop as an API Endpoint ---
@app.post('/api/jarvis')
async def handle_jarvis_request(audio: UploadFile = File(...)):
    """
    This is the main endpoint for the Jarvis assistant.
    It receives an audio file, processes it, and returns the final plan.
    """
    # 1. Save the uploaded audio file
    temp_audio_path = "Data/temp_command.wav"
    with open(temp_audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
    
    # 2. Transcribe the audio to text
    user_query = transcribe_audio(temp_audio_path)
    if not user_query:
        return {"response": "I'm sorry, I didn't catch that.", "commands": []}
        
    print(f"🎧 You said: {user_query}")
    
    # 3. Start the agentic loop
    messages = [{"role": "user", "content": user_query}]
    while True:
        print("🧠 Thinking...")
        ai_response_message = await get_ai_response(messages)

        if ai_response_message.tool_calls:
            print(f"🛠️ AI wants to use tools: {[tc.function.name for tc in ai_response_message.tool_calls]}")
            messages.append(ai_response_message)
            
            tool_results = await asyncio.gather(*[execute_tool_call(tc) for tc in ai_response_message.tool_calls])
            
            for i, tool_call in enumerate(ai_response_message.tool_calls):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": str(tool_results[i]),
                })
            # Go back to the brain to process the tool's result
            continue 
        else:
            # If the AI responds with text, this is our final answer.
            final_response_text = ai_response_message.content
            print(f"🤖 Jarvis: {final_response_text}")
            
            # In a real app, we would generate TTS audio and send it back.
            # For now, we'll send back the text and the final (empty) command list.
            return {
                "response": final_response_text,
                "commands": [] # The commands were already executed on the server side
            }

@app.on_event("startup")
async def startup_event():
    """This function runs once when the server starts up."""
    print("🤖 Jarvis Brain Server is starting up...")
    print("🔄 Syncing installed app list from device...")
    # We run this synchronously as it's a one-time startup task
    sync_app_list()
    print("✅ Sync complete. Server is ready.")

# To run this server, use the command: uvicorn server:app --reload
