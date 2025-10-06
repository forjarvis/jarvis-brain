import json
from utils.skills import adb_skills, assistant_skills, information_skills, api_skills

# The complete and correct Skill Registry
SKILL_REGISTRY = {
    # Information Gathering
    "silent_web_search": information_skills.silent_web_search,
    "visible_web_search": adb_skills.visible_web_search,
    "analyze_screen": information_skills.analyze_screen,
    "battery_stats": information_skills.battery_stats, "get_brightness": information_skills.get_brightness,
    # API Placeholders
    "acc_click": api_skills.acc_click, "acc_type": api_skills.acc_type, "press_back": api_skills.press_back,
    "press_home": api_skills.press_home, "open_notifications": api_skills.open_notifications,
    "lock_device": api_skills.lock_device,
    # Direct Device Skills
    "take_screenshot": adb_skills.take_screenshot, "create_folder": adb_skills.create_folder,
    "move_file": adb_skills.move_file, "type_text": adb_skills.type_text,
    "send_keyevent": adb_skills.send_keyevent, "force_stop_app": adb_skills.force_stop_app,
    "clear_app_data": adb_skills.clear_app_data, "set_brightness": adb_skills.set_brightness,
    "reboot_device": adb_skills.reboot_device,
    # Internal Assistant Skills
    "open_app": assistant_skills.open_app, "save_fact_to_memory": assistant_skills.save_fact_to_memory,
    "wait": assistant_skills.wait, "wait_for_text": assistant_skills.wait_for_text,
    "class_mode_on": assistant_skills.class_mode_on, "class_mode_off": assistant_skills.class_mode_off,
}

async def execute_tool_call(tool_call):
    """Executes a single tool call from the AI with robust argument handling."""
    skill_name = tool_call.function.name
    
    # This handles all argument cases, including no arguments.
    args = {}
    if tool_call.function.arguments and tool_call.function.arguments.strip():
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Could not parse arguments for {skill_name}. Proceeding without them.")
            args = {}

    if skill_name in SKILL_REGISTRY:
        skill_function = SKILL_REGISTRY[skill_name]
        print(f"▶️ Calling Skill: {skill_name} with args: {args}")
        try:
            # This is the definitive fix for all argument-related TypeErrors.
            # It correctly calls the function whether args is empty or populated.
            result = await skill_function(**args)
            return result
        except Exception as e:
            print(f"❌ Error executing skill '{skill_name}': {e}")
            return f"Error: {e}"
    else:
        print(f"❓ Unknown skill called by AI: '{skill_name}'")
        return f"Unknown skill '{skill_name}'."
