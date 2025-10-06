import asyncio
import json

from core.audio_manager import listen_and_record
from utils.stt_processor import transcribe_audio
from brain.orchestrator import get_ai_response
from device_control.command_executor import execute_tool_call
from core.audio_manager_tts_only import speak
from utils.app_manager import sync_app_list

async def main_loop():
    """The main agentic loop for the assistant."""
    messages = []
    while True:
        print("\n" + "="*50)
        recorded_audio_path = await asyncio.to_thread(listen_and_record)
        if not recorded_audio_path: continue

        user_query = transcribe_audio(recorded_audio_path)
        if not user_query: continue
        
        print(f"🎧 You said: {user_query}")
        messages.append({"role": "user", "content": user_query})

        # --- The Agentic Loop ---
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
                # If the AI responds with text, speak it and end the turn.
                final_response = ai_response_message.content
                print(f"🤖 Jarvis: {final_response}")
                await speak(final_response)
                messages.append({"role": "assistant", "content": final_response})
                break # Exit the inner loop and wait for the next hotword

async def startup():
    print("🤖 Assistant is starting up...")
    sync_app_list()
    await main_loop()

if __name__ == "__main__":
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        print("\n🤖 Shutting down assistant. Goodbye!")
