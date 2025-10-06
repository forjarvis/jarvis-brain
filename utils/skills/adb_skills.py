import asyncio
import subprocess
from urllib.parse import quote_plus
async def _execute_shell_command(command: str):
    """Helper to run a single adb shell command."""
    full_command = f"adb shell {command}"
    process = await asyncio.create_subprocess_shell(
        full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print(f"⚠️ Error executing '{full_command}': {stderr.decode().strip()}")
        return None
    else:
        print(f"✅ Successfully executed: '{full_command}'")
        return stdout.decode().strip() if stdout else ""

async def take_screenshot(**kwargs):
    return await _execute_shell_command("screencap -p /sdcard/Pictures/screenshot_$(date +%s).png")

async def type_text(**kwargs):
    text_to_type = kwargs.get("text_to_type")
    if not text_to_type: return "Error: text_to_type argument missing."
    sanitized_text = str(text_to_type).replace("'", "'\\''").replace(" ", "%s")
    return await _execute_shell_command(f"input text {sanitized_text}")

async def send_keyevent(**kwargs):
    keycode = kwargs.get("keycode")
    if not keycode: return "Error: keycode argument missing."
    return await _execute_shell_command(f"input keyevent {keycode}")

async def force_stop_app(**kwargs):
    package_name = kwargs.get("package_name")
    if not package_name: return "Error: package_name argument missing."
    return await _execute_shell_command(f"am force-stop {package_name}")

async def clear_app_data(**kwargs):
    package_name = kwargs.get("package_name")
    if not package_name: return "Error: package_name argument missing."
    return await _execute_shell_command(f"pm clear {package_name}")

async def set_brightness(**kwargs):
    level = kwargs.get("level")
    if not level: return "Error: level argument missing."
    return await _execute_shell_command(f"settings put system screen_brightness {level}")
    
async def reboot_device(**kwargs):
    process = await asyncio.create_subprocess_shell(
        "adb reboot", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    await process.communicate()

async def create_folder(**kwargs):
    folder_path = kwargs.get("folder_path")
    if not folder_path: return "Error: folder_path argument missing."
    return await _execute_shell_command(f"mkdir -p {folder_path}")

async def move_file(**kwargs):
    source_path = kwargs.get("source_path")
    destination_path = kwargs.get("destination_path")
    if not source_path or not destination_path: return "Error: file paths missing."
    return await _execute_shell_command(f"mv {source_path} {destination_path}")

# Add this new function at the bottom of the file
async def visible_web_search(**kwargs):
    """Opens the browser on the device to perform a visible Google search."""
    query = kwargs.get("query")
    if not query: return "Error: query argument missing."
    
    print(f"🖥️ Performing visible web search for: '{query}'")
    # URL encode the query to handle spaces and special characters
    encoded_query = quote_plus(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    
    # Use the adb command to open the URL in the browser
    return await _execute_shell_command(f"am start -a android.intent.action.VIEW -d '{url}'")
