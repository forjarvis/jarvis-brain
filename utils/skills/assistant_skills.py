import asyncio
import json
import os
import time
import subprocess
import cv2
import easyocr
from utils.skills.adb_skills import _execute_shell_command

# --- OCR Setup ---
print("OCR: Initializing EasyOCR reader... (This may take a moment on first run)")
reader = easyocr.Reader(['en'])
print("OCR: Reader initialized.")

# --- App Dictionary ---
try:
    with open("Data/app_packages.json", "r") as f:
        APP_DICTIONARY = json.load(f)
except Exception:
    APP_DICTIONARY = {}

# --- Skill Implementations ---
async def open_app(**kwargs):
    app_name = kwargs.get("app_name")
    if not app_name: return "Error: app_name argument missing."
    app_key = app_name.lower().strip().replace(" ", "")
    if app_key in APP_DICTIONARY:
        package_name = APP_DICTIONARY[app_key]
        return await _execute_shell_command(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
    else:
        print(f"⚠️ App '{app_name}' not found in dictionary.")
        return f"App '{app_name}' not found"

async def save_fact_to_memory(**kwargs):
    fact = kwargs.get("fact")
    if not fact: return "Error: fact argument missing."
    print(f"🧠 Remembering fact: '{fact}'")
    try:
        try:
            with open("Data/long_term_memory.json", "r") as f: memory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): memory = {"facts": []}
        if fact not in memory["facts"]: memory["facts"].append(fact)
        with open("Data/long_term_memory.json", "w") as f: json.dump(memory, f, indent=4)
        return "Fact saved successfully."
    except Exception as e:
        print(f"⚠️ Failed to save fact to memory: {e}")
        return "Failed to save fact."

async def wait(**kwargs):
    seconds = kwargs.get("seconds")
    if not seconds: return "Error: seconds argument missing."
    print(f"⏳ Waiting for {seconds} seconds...")
    await asyncio.sleep(float(seconds))

def _is_text_visible(text_to_find: str) -> bool:
    subprocess.run("adb shell screencap -p /sdcard/screen.png", shell=True)
    subprocess.run("adb pull /sdcard/screen.png .", shell=True)
    try:
        img = cv2.imread("screen.png")
        if img is None: return False
        results = reader.readtext(img, detail=0, paragraph=True)
        for line in results:
            if text_to_find.lower() in line.lower():
                print(f"✅ Found text: '{text_to_find}'")
                return True
        return False
    finally:
        if os.path.exists("screen.png"): os.remove("screen.png")

async def wait_for_text(**kwargs):
    text_to_find = kwargs.get("text_to_find")
    if not text_to_find: return "Error: text_to_find argument missing."
    print(f"👀 Waiting for text: '{text_to_find}'...")
    max_wait_time = 15; start_time = time.time()
    while time.time() - start_time < max_wait_time:
        if await asyncio.to_thread(_is_text_visible, text_to_find):
            return "Text found."
        await asyncio.sleep(1)
    print(f"⚠️ Timed out waiting for text: '{text_to_find}'")
    return "Text not found."
    
async def class_mode_on(**kwargs):
    await _execute_shell_command("cmd audio set_ringer_mode 1")
    await _execute_shell_command("media volume --stream 3 --set 0")
    await _execute_shell_command("media volume --stream 1 --set 0")

async def class_mode_off(**kwargs):
    await _execute_shell_command("cmd audio set_ringer_mode 2")
    await _execute_shell_command("media volume --stream 3 --set 7")
    await _execute_shell_command("media volume --stream 1 --set 4")
