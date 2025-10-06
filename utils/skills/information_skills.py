import asyncio
import os
import subprocess
import requests
import base64
import io
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from PIL import Image
from utils.skills.adb_skills import _execute_shell_command
from groq import AsyncGroq
from serpapi import GoogleSearch
# --- Configuration ---
config = dotenv_values(".env")
# Initialize the SambaNova client, which will be used for vision
client = AsyncGroq(
    api_key=config.get("GroqAPIKey"),
)
SCREENSHOT_PATH = "screen_for_vision.png"

SERPAPI_KEY = config.get("SerpApiKey")

# --- Web Search Skill ---
def _silent_web_search(query: str) -> str:
    """Synchronous web search function using SerpApi for reliable results."""
    print(f"🤫 Performing professional web search for: '{query}'")
    try:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Look for a direct answer (knowledge graph) first
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "answer_box" in results and "snippet" in results["answer_box"]:
            return results["answer_box"]["snippet"]
        
        # If no direct answer, return the snippet of the first organic result
        if "organic_results" in results and len(results["organic_results"]) > 0:
            return results["organic_results"][0].get("snippet", "No snippet available.")

        return "Sorry sir, I couldn't find a direct answer for that query."
        
    except Exception as e:
        print(f"❌ Web search failed: {e}")
        return "Sorry sir, I had trouble connecting to the search API."

async def silent_web_search(**kwargs):
    query = kwargs.get("query")
    if not query: return "Error: query argument missing."
    return await asyncio.to_thread(_silent_web_search, query)


# --- NEW: Helper function to encode image for the API ---
def _encode_image_to_base64(image: Image.Image) -> str:
    """Converts a PIL Image to a base64 encoded string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- Visual Analysis Skill (Upgraded) ---
async def analyze_screen(**kwargs):
    question = kwargs.get("question")
    if not question: return "Error: question argument missing."
    print(f"👀 Analyzing screen with question: '{question}'")
    try:
        # 1. Capture the screen (no changes here)
        subprocess.run(f"adb shell screencap -p /sdcard/{SCREENSHOT_PATH}", shell=True, check=True)
        subprocess.run(f"adb pull /sdcard/{SCREENSHOT_PATH} .", shell=True, check=True)

        # 2. Open and encode the image for the API
        img = Image.open(SCREENSHOT_PATH)
        base64_image = _encode_image_to_base64(img)
        img.close() # Release file lock immediately

        # 3. Call the SambaNova API with the image and question
        response = await client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        answer = response.choices[0].message.content.strip()
        print(f"👁️ SambaNova Vision answered: '{answer}'")
        return answer
        
    except Exception as e:
        print(f"❌ An error occurred during visual analysis: {e}")
        return f"Sorry sir, I encountered an error analyzing the screen: {e}"
    finally:
        # 4. Clean up the screenshot file (no changes here)
        if os.path.exists(SCREENSHOT_PATH):
            os.remove(SCREENSHOT_PATH)

# --- Device Info Skills ---
async def battery_stats(**kwargs):
    return await _execute_shell_command("dumpsys battery")

async def get_brightness(**kwargs):
    return await _execute_shell_command("settings get system screen_brightness")
